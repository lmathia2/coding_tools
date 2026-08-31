import sqlite3

from support import TenantCase


class AuditTests(TenantCase):
    def events(self, tenant=1):
        actor = 1 if tenant == 1 else 2
        response = self.call('GET', '/audit', actor=actor, tenant=tenant)
        self.assertEqual(200, response.status)
        return response.body

    def test_audit_reads_are_tenant_scoped(self):
        self.assertTrue(all(row['tenant_id'] == 1 for row in self.events(1)))
        self.assertTrue(all(row['tenant_id'] == 2 for row in self.events(2)))

    def test_denial_is_one_sanitized_request_tenant_event(self):
        before_a, before_b = self.events(1), self.events(2)
        self.call('GET', '/issues/' + str(self.b))
        events = self.events(1)[len(before_a):]
        self.assertEqual(1, len(events))
        event = events[0]
        self.assertEqual((1, 1, 'access.denied', None, {'code': 'not_found'}),
                         (event['tenant_id'], event['actor_id'], event['action'], event['resource_id'], event['details']))
        self.assertEqual(before_b, self.events(2))

    def test_bulk_failure_does_not_emit_success_or_multiple_denials(self):
        before = len(self.events())
        self.call('POST', '/issues/bulk', {'ids': [self.a, 999999], 'changes': {'title': 'No'}})
        events = self.events()[before:]
        self.assertEqual(['access.denied'], [row['action'] for row in events])
        self.assertEqual({'code': 'not_found'}, events[0]['details'])

    def test_bulk_success_has_one_summary_event(self):
        before = len(self.events())
        self.call('POST', '/issues/bulk', {'ids': [self.a], 'changes': {'status': 'closed'}})
        events = self.events()[before:]
        self.assertEqual(['issues.bulk_updated'], [row['action'] for row in events])
        self.assertEqual({'count': 1}, events[0]['details'])

    def test_unaffiliated_and_revoked_callers_cannot_pollute_tenant_audit(self):
        before = self.events()
        self.call('GET', '/issues', actor=4)
        self.change_membership(1, 3, active=0)
        self.call('GET', '/issues', actor=3)
        self.assertEqual(before, self.events())

    def test_forbidden_member_action_has_sanitized_audit(self):
        before = len(self.events())
        self.call('POST', '/projects', {'name': 'Sensitive request body'}, actor=3)
        events = self.events()[before:]
        self.assertEqual(1, len(events))
        self.assertEqual({'code': 'forbidden'}, events[0]['details'])
        self.assertIsNone(events[0]['resource_id'])

    def test_worker_denial_is_job_tenant_audit_with_no_success(self):
        job = self.call('POST', '/exports', actor=3).body['id']
        self.change_membership(1, 3, active=0)
        self.app.exports.run_next()
        events = [row for row in self.events() if row['resource_id'] == job and row['action'].startswith('export.')]
        self.assertEqual(['export.queued', 'export.denied'], [row['action'] for row in events])
        self.assertEqual({'reason': 'authorization_revoked'}, events[-1]['details'])

    def test_audit_write_failure_rolls_back_business_update(self):
        before = self.snapshot()
        self.app.db.connection.execute("CREATE TRIGGER reject_audit BEFORE INSERT ON audit "
                                       "BEGIN SELECT RAISE(ABORT, 'injected audit failure'); END")
        with self.assertRaises(sqlite3.IntegrityError):
            self.call('PATCH', '/issues/' + str(self.a), {'title': 'Must roll back'})
        self.assertEqual(before, self.snapshot())
