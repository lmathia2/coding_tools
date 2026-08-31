"""Solution-owned regression coverage; independent of evaluator discovery."""

import unittest

from issuehub import App, RequestContext
from issuehub.errors import DomainError


class IsolationRegressionTests(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.addCleanup(self.app.close)
        with self.app.db.transaction():
            self.app.db.connection.executemany('INSERT INTO tenants VALUES(?,?)',
                                               [(17, 'North'), (29, 'South')])
            self.app.db.connection.executemany('INSERT INTO users VALUES(?,?)',
                                               [(101, 'Owner'), (202, 'Reader')])
            self.app.db.connection.executemany('INSERT INTO memberships VALUES(?,?,?,1)',
                                               [(17, 101, 'admin'), (29, 101, 'admin'), (17, 202, 'viewer')])
        self.north = RequestContext(101, 17)
        self.south = RequestContext(101, 29)
        self.reader = RequestContext(202, 17)
        self.north_project = self.app.service.create_project(self.north, 'North project')['id']
        self.south_project = self.app.service.create_project(self.south, 'South project')['id']
        self.north_issue = self.app.service.create_issue(self.north, self.north_project, 'same prefix North')['id']
        self.south_issue = self.app.service.create_issue(self.south, self.south_project, 'same prefix South')['id']

    def test_direct_viewer_write_is_forbidden(self):
        with self.assertRaises(DomainError) as caught:
            self.app.service.update_issue(self.reader, self.north_issue, {'title': 'No'})
        self.assertEqual(403, caught.exception.status)

    def test_actor_can_switch_tenants_without_query_cache_leak(self):
        for context, expected in ((self.north, self.north_issue), (self.south, self.south_issue), (self.north, self.north_issue)):
            self.assertEqual([expected], [row['id'] for row in self.app.service.list_issues(context, 'same prefix')])

    def test_warm_detail_does_not_authorize_foreign_context(self):
        self.app.service.get_issue(self.south, self.south_issue)
        with self.assertRaises(DomainError) as caught:
            self.app.service.get_issue(self.north, self.south_issue)
        self.assertEqual(404, caught.exception.status)

    def test_bulk_failure_rolls_back_prior_target_and_success_audit(self):
        before = len(self.app.service.list_audit(self.north))
        with self.assertRaises(DomainError):
            self.app.service.bulk_update(self.north, [self.north_issue, 90000], {'status': 'closed'})
        self.assertEqual('open', self.app.service.get_issue(self.north, self.north_issue)['status'])
        events = self.app.service.list_audit(self.north)[before:]
        self.assertEqual(['access.denied'], [row['action'] for row in events])

    def test_relationship_move_is_scoped(self):
        with self.assertRaises(DomainError):
            self.app.service.update_issue(self.north, self.north_issue, {'project_id': self.south_project})
        self.assertEqual(self.north_project, self.app.service.get_issue(self.north, self.north_issue)['project_id'])

    def test_revoked_queued_job_has_no_bytes(self):
        job = self.app.exports.enqueue(self.reader)
        self.app.db.connection.execute('UPDATE memberships SET active=0 WHERE tenant_id=17 AND user_id=202')
        self.assertEqual('denied', self.app.exports.run_next()['state'])
        row = self.app.db.connection.execute('SELECT content,error FROM export_jobs WHERE id=?', (job['id'],)).fetchone()
        self.assertEqual((None, 'authorization_revoked'), tuple(row))

    def test_ready_job_checks_current_membership_at_download(self):
        job = self.app.exports.enqueue(self.reader)
        self.app.exports.run_next()
        self.app.db.connection.execute('UPDATE memberships SET active=0 WHERE tenant_id=17 AND user_id=202')
        with self.assertRaises(DomainError) as caught:
            self.app.exports.download(self.reader, job['id'])
        self.assertEqual(403, caught.exception.status)

    def test_export_csv_is_scoped_and_owner_only(self):
        job = self.app.exports.enqueue(self.reader)
        self.app.exports.run_next()
        self.assertNotIn('South', self.app.exports.download(self.reader, job['id']))
        with self.assertRaises(DomainError) as caught:
            self.app.exports.download(self.north, job['id'])
        self.assertEqual(404, caught.exception.status)


if __name__ == '__main__':
    unittest.main()
