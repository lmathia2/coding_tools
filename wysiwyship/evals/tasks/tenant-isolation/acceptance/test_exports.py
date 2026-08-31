import csv
import io

from issuehub import RequestContext

from support import TenantCase


class ExportTests(TenantCase):
    def enqueue(self, actor=1, tenant=1, body=None):
        response = self.call('POST', '/exports', body, actor=actor, tenant=tenant)
        self.assertEqual(202, response.status)
        return response.body['id']

    def test_export_is_tenant_scoped_even_without_filter(self):
        export_id = self.enqueue()
        self.app.exports.run_next()
        response = self.call('GET', '/exports/{}/download'.format(export_id))
        rows = list(csv.DictReader(io.StringIO(response.body)))
        self.assertEqual([str(self.a)], [row['id'] for row in rows])
        self.assertNotIn('Boreal', response.body)

    def test_foreign_filter_cannot_be_enqueued(self):
        before = self.snapshot()
        self.assertMissing(self.call('POST', '/exports', {'project_id': self.pb}))
        self.assertEqual(before, self.snapshot())

    def test_export_metadata_and_download_hide_foreign_jobs(self):
        export_id = self.enqueue(actor=2, tenant=2)
        self.app.exports.run_next()
        for suffix in ('', '/download'):
            with self.subTest(suffix=suffix):
                foreign = self.call('GET', '/exports/{}{}'.format(export_id, suffix))
                absent = self.call('GET', '/exports/999999' + suffix)
                self.assertMissing(foreign)
                self.assertEqual((absent.status, absent.body), (foreign.status, foreign.body))

    def test_other_member_including_admin_cannot_read_owned_export(self):
        export_id = self.enqueue(actor=3)
        self.app.exports.run_next()
        for actor in (1, 2, 5):
            for suffix in ('', '/download'):
                with self.subTest(actor=actor, suffix=suffix):
                    self.assertMissing(self.call('GET', '/exports/{}{}'.format(export_id, suffix), actor=actor))
        self.assertEqual(200, self.call('GET', '/exports/{}/download'.format(export_id), actor=3).status)

    def test_revoked_queued_export_becomes_terminal_denied_without_bytes(self):
        export_id = self.enqueue(actor=3)
        self.change_membership(1, 3, active=0)
        outcome = self.app.exports.run_next()
        self.assertEqual(('denied', 'authorization_revoked'), (outcome['state'], outcome['error']))
        self.assertIsNone(self.app.db.connection.execute('SELECT content FROM export_jobs WHERE id=?', (export_id,)).fetchone()[0])
        self.assertIsNone(self.app.exports.run_next())
        self.change_membership(1, 3, active=1)
        self.assertEqual(409, self.call('GET', '/exports/{}/download'.format(export_id), actor=3).status)

    def test_deleted_membership_also_denies_execution(self):
        self.enqueue(actor=3)
        self.app.db.connection.execute('DELETE FROM memberships WHERE tenant_id=1 AND user_id=3')
        self.assertEqual('denied', self.app.exports.run_next()['state'])

    def test_ready_export_cannot_bypass_later_revocation(self):
        export_id = self.enqueue(actor=3)
        self.app.exports.run_next()
        self.assertEqual(200, self.call('GET', '/exports/{}/download'.format(export_id), actor=3).status)
        self.change_membership(1, 3, active=0)
        self.assertEqual(403, self.call('GET', '/exports/{}/download'.format(export_id), actor=3).status)
        self.assertEqual(403, self.call('GET', '/exports/' + str(export_id), actor=3).status)

    def test_membership_in_other_tenant_does_not_authorize_execution(self):
        self.enqueue()
        self.change_membership(1, 1, active=0)
        self.assertEqual('denied', self.app.exports.run_next()['state'])

    def test_worker_continues_after_denied_job_and_preserves_fifo(self):
        first = self.enqueue(actor=3)
        second = self.enqueue(actor=2, tenant=2)
        self.change_membership(1, 3, active=0)
        one, two = self.app.exports.run_next(), self.app.exports.run_next()
        self.assertEqual((first, 'denied'), (one['id'], one['state']))
        self.assertEqual((second, 'ready'), (two['id'], two['state']))
        self.assertIsNone(self.app.exports.run_next())

    def test_worker_uses_execution_time_data_not_enqueue_snapshot(self):
        export_id = self.enqueue()
        self.call('PATCH', '/issues/' + str(self.a), {'title': 'Updated after enqueue'})
        self.app.exports.run_next()
        self.assertIn('Updated after enqueue', self.call('GET', '/exports/{}/download'.format(export_id)).body)

    def test_viewer_can_export_and_metadata_never_contains_content(self):
        export_id = self.enqueue(actor=3, body={'project_id': self.pa})
        expected = {'id', 'tenant_id', 'requested_by', 'project_id', 'state', 'error'}
        self.assertEqual(expected, set(self.call('GET', '/exports/' + str(export_id), actor=3).body))
        self.assertEqual('ready', self.app.exports.run_next()['state'])
        self.assertEqual(expected, set(self.call('GET', '/exports/' + str(export_id), actor=3).body))

    def test_direct_export_calls_enforce_scope_and_fresh_membership(self):
        export_id = self.enqueue(actor=2, tenant=2)
        self.assertDomain(404, self.app.exports.get, RequestContext(1, 1), export_id)
        self.assertDomain(403, self.app.exports.enqueue, RequestContext(4, 1))
        self.app.exports.run_next()
        self.change_membership(2, 2, active=0)
        self.assertDomain(403, self.app.exports.download, RequestContext(2, 2), export_id)

    def test_role_downgrade_to_viewer_keeps_legitimate_export_access(self):
        export_id = self.enqueue(actor=2)
        self.change_membership(1, 2, role='viewer')
        self.assertEqual('ready', self.app.exports.run_next()['state'])
        self.assertEqual(200, self.call('GET', '/exports/{}/download'.format(export_id), actor=2).status)
