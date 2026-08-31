from issuehub import RequestContext

from support import TenantCase


class BoundaryTests(TenantCase):
    def test_unknown_or_missing_identity(self):
        for actor in (None, 999, True, '1'):
            with self.subTest(actor=actor):
                self.assertEqual(401, self.call('GET', '/issues', actor=actor).status)

    def test_explicit_tenant_is_required(self):
        for tenant in (None, True, '1', 0, -1):
            with self.subTest(tenant=tenant):
                self.assertEqual(400, self.call('GET', '/issues', tenant=tenant).status)

    def test_no_membership_or_unknown_tenant(self):
        for actor, tenant in ((4, 1), (3, 2), (1, 999)):
            with self.subTest(actor=actor, tenant=tenant):
                self.assertEqual(403, self.call('GET', '/issues', actor=actor, tenant=tenant).status)

    def test_roles_cover_every_mutating_route(self):
        before = self.snapshot()
        cases = [
            ('POST', '/projects', {'name': 'No'}),
            ('POST', '/issues', {'project_id': self.pa, 'title': 'No'}),
            ('PATCH', '/issues/' + str(self.a), {'status': 'closed'}),
            ('POST', '/issues/' + str(self.a) + '/comments', {'text': 'No'}),
            ('POST', '/issues/bulk', {'ids': [self.a], 'changes': {'status': 'closed'}}),
            ('GET', '/audit', None),
        ]
        for method, path, body in cases:
            with self.subTest(path=path):
                self.assertEqual(403, self.call(method, path, body, actor=3).status)
        self.assertEqual(before, self.snapshot())

    def test_editor_cannot_create_project_or_read_audit(self):
        self.assertEqual(403, self.call('POST', '/projects', {'name': 'No'}, actor=2).status)
        self.assertEqual(403, self.call('GET', '/audit', actor=2).status)

    def test_role_is_per_requested_tenant(self):
        self.assertEqual(200, self.call('GET', '/issues/' + str(self.b), tenant=2).status)
        self.assertEqual(403, self.call('PATCH', '/issues/' + str(self.b), {'status': 'closed'}, tenant=2).status)

    def test_revocation_applies_before_warm_cache_reads(self):
        self.call('GET', '/issues', actor=3)
        self.call('GET', '/issues/' + str(self.a), actor=3)
        self.change_membership(1, 3, active=0)
        for path in ('/issues', '/issues/' + str(self.a), '/projects'):
            with self.subTest(path=path):
                self.assertEqual(403, self.call('GET', path, actor=3).status)

    def test_role_downgrade_is_immediate(self):
        self.call('GET', '/issues/' + str(self.a), actor=2)
        self.change_membership(1, 2, role='viewer')
        self.assertEqual(403, self.call('PATCH', '/issues/' + str(self.a), {'title': 'No'}, actor=2).status)
        self.assertEqual(200, self.call('GET', '/issues/' + str(self.a), actor=2).status)

    def test_direct_service_cannot_bypass_checks(self):
        self.assertDomain(403, self.app.service.update_issue, RequestContext(3, 1), self.a, {'title': 'No'})
        self.assertDomain(404, self.app.service.get_issue, RequestContext(1, 1), self.b)
        self.assertDomain(403, self.app.service.list_issues, RequestContext(4, 1))

    def test_membership_deletion_is_immediate(self):
        self.call('GET', '/issues', actor=3)
        self.app.db.connection.execute('DELETE FROM memberships WHERE tenant_id=1 AND user_id=3')
        self.assertEqual(403, self.call('GET', '/issues', actor=3).status)
