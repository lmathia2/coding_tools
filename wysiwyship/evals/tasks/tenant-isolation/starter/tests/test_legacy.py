import csv
import io
import tempfile
import unittest
from pathlib import Path

from issuehub import App, RequestContext
from issuehub.seed import seed_demo


class LegacyWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.app = App()
        seed_demo(self.app)

    def tearDown(self):
        self.app.close()

    def request(self, method, path, body=None, query=None, actor=1):
        return self.app.request(method, path, actor_id=actor, tenant_id=1,
                                body=body, query=query)

    def test_seed_is_idempotent(self):
        seed_demo(self.app)
        self.assertEqual(1, len(self.request('GET', '/projects').body))

    def test_project_creation(self):
        response = self.request('POST', '/projects', {'name': '  Support  '})
        self.assertEqual(201, response.status)
        self.assertEqual('Support', response.body['name'])

    def test_create_issue_and_get(self):
        response = self.request('POST', '/issues', {'project_id': 1, 'title': '  Ship  '}, actor=2)
        self.assertEqual(201, response.status)
        self.assertEqual({'id': response.body['id'], 'project_id': 1, 'title': 'Ship',
                          'status': 'open', 'created_by': 2}, response.body)
        self.assertEqual(response.body, self.request('GET', '/issues/' + str(response.body['id'])).body)

    def test_patch_invalidate_detail(self):
        self.request('GET', '/issues/1')
        self.assertEqual(200, self.request('PATCH', '/issues/1', {'status': 'closed'}).status)
        self.assertEqual('closed', self.request('GET', '/issues/1').body['status'])

    def test_search_is_case_insensitive_literal_substring(self):
        self.assertEqual(1, len(self.request('GET', '/issues', query={'q': 'RELEASE'}).body))
        self.assertEqual([], self.request('GET', '/issues', query={'q': '%'}).body)

    def test_filters(self):
        self.assertEqual(1, len(self.request('GET', '/issues', query={'project_id': 1, 'status': 'open'}).body))
        self.assertEqual([], self.request('GET', '/issues', query={'status': 'closed'}).body)

    def test_cache_returns_independent_copies(self):
        self.request('GET', '/issues').body[0]['title'] = 'Caller mutated'
        self.assertEqual('Write release notes', self.request('GET', '/issues').body[0]['title'])

    def test_comments(self):
        comment = self.request('POST', '/issues/1/comments', {'text': 'Looks good'}, actor=2)
        self.assertEqual(201, comment.status)
        self.assertEqual([comment.body], self.request('GET', '/issues/1/comments', actor=3).body)

    def test_move_to_same_workspace_project(self):
        project = self.request('POST', '/projects', {'name': 'Maintenance'}).body
        self.assertEqual(project['id'], self.request('PATCH', '/issues/1', {'project_id': project['id']}).body['project_id'])

    def test_bulk_success_preserves_input_order(self):
        other = self.request('POST', '/issues', {'project_id': 1, 'title': 'Other'}).body['id']
        response = self.request('POST', '/issues/bulk', {'ids': [other, 1], 'changes': {'status': 'closed'}})
        self.assertEqual(200, response.status)
        self.assertEqual([other, 1], [row['id'] for row in response.body])
        self.assertTrue(all(row['status'] == 'closed' for row in response.body))

    def test_validation(self):
        for body in ({'title': ''}, {'status': 'invalid'}, {'id': 2}, {}):
            with self.subTest(body=body):
                self.assertEqual(400, self.request('PATCH', '/issues/1', body).status)

    def test_bulk_duplicate_validation(self):
        self.assertEqual(400, self.request('POST', '/issues/bulk', {
            'ids': [1, 1], 'changes': {'status': 'closed'}}).status)

    def test_missing_resource_and_identity(self):
        self.assertEqual(404, self.request('GET', '/issues/999').status)
        self.assertEqual(401, self.request('GET', '/issues', actor=999).status)

    def test_audit_for_successful_write(self):
        self.request('POST', '/issues/1/comments', {'text': 'Review'})
        events = self.request('GET', '/audit').body
        self.assertTrue(any(row['action'] == 'comment.created' for row in events))

    def test_export_lifecycle_and_csv_escaping(self):
        self.request('PATCH', '/issues/1', {'title': 'Hello, "CSV"\nnext line'})
        response = self.request('POST', '/exports')
        self.assertEqual(202, response.status)
        path = '/exports/{}/download'.format(response.body['id'])
        self.assertEqual(409, self.request('GET', path).status)
        self.assertEqual('ready', self.app.exports.run_next()['state'])
        download = self.request('GET', path)
        rows = list(csv.DictReader(io.StringIO(download.body)))
        self.assertEqual('Hello, "CSV"\nnext line', rows[0]['title'])
        self.assertIsNone(self.app.exports.run_next())

    def test_direct_service_contract(self):
        context = RequestContext(2, 1)
        issue = self.app.service.create_issue(context, 1, 'Direct service')
        self.assertEqual(issue, self.app.service.get_issue(context, issue['id']))

    def test_jobs_and_data_survive_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'issues.sqlite'
            first = App(path)
            seed_demo(first)
            job = first.exports.enqueue(RequestContext(1, 1))
            first.close()
            second = App(path)
            try:
                self.assertEqual(job['id'], second.exports.run_next()['id'])
                self.assertIn('Write release notes', second.exports.download(RequestContext(1, 1), job['id']))
            finally:
                second.close()


if __name__ == '__main__':
    unittest.main()
