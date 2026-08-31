from support import TenantCase


class WriteIntegrityTests(TenantCase):
    def test_foreign_update_and_absent_update_match(self):
        before = self.snapshot()
        foreign = self.call('PATCH', '/issues/' + str(self.b), {'title': 'No'})
        absent = self.call('PATCH', '/issues/999999', {'title': 'No'})
        self.assertMissing(foreign)
        self.assertEqual((foreign.status, foreign.body), (absent.status, absent.body))
        self.assertEqual(before, self.snapshot())

    def test_create_issue_rejects_foreign_parent(self):
        before = self.snapshot()
        self.assertMissing(self.call('POST', '/issues', {'project_id': self.pb, 'title': 'No'}))
        self.assertEqual(before, self.snapshot())

    def test_move_cannot_change_tenant(self):
        before = self.snapshot()
        self.assertMissing(self.call('PATCH', '/issues/' + str(self.a), {'project_id': self.pb}))
        self.assertEqual(before, self.snapshot())

    def test_comment_cannot_attach_to_foreign_issue(self):
        before = self.snapshot()
        self.assertMissing(self.call('POST', '/issues/' + str(self.b) + '/comments', {'text': 'No'}))
        self.assertEqual(before, self.snapshot())

    def test_bulk_with_foreign_id_is_atomic(self):
        before = self.snapshot()
        self.assertMissing(self.call('POST', '/issues/bulk', {
            'ids': [self.a, self.b], 'changes': {'status': 'closed'}}))
        self.assertEqual(before, self.snapshot())

    def test_bulk_with_missing_later_id_is_atomic_including_cache(self):
        old = self.call('GET', '/issues/' + str(self.a)).body
        before = self.snapshot()
        self.assertMissing(self.call('POST', '/issues/bulk', {
            'ids': [self.a, 999999], 'changes': {'status': 'closed'}}))
        self.assertEqual(before, self.snapshot())
        self.assertEqual(old, self.call('GET', '/issues/' + str(self.a)).body)

    def test_bulk_foreign_destination_is_atomic(self):
        other = self.call('POST', '/issues', {'project_id': self.pa, 'title': 'Other'}).body['id']
        before = self.snapshot()
        self.assertMissing(self.call('POST', '/issues/bulk', {
            'ids': [self.a, other], 'changes': {'project_id': self.pb, 'title': 'No'}}))
        self.assertEqual(before, self.snapshot())

    def test_successful_batch_preserves_order_and_invalidates_cache(self):
        other = self.call('POST', '/issues', {'project_id': self.pa, 'title': 'Other'}).body['id']
        self.call('GET', '/issues', query={'status': 'closed'})
        self.call('GET', '/issues/' + str(self.a))
        response = self.call('POST', '/issues/bulk', {
            'ids': [other, self.a], 'changes': {'status': 'closed'}})
        self.assertEqual(200, response.status)
        self.assertEqual([other, self.a], [i['id'] for i in response.body])
        self.assertEqual([self.a, other], [i['id'] for i in self.call('GET', '/issues', query={'status': 'closed'}).body])
        self.assertEqual('closed', self.call('GET', '/issues/' + str(self.a)).body['status'])
        self.assertEqual('open', self.call('GET', '/issues/' + str(self.b), tenant=2).body['status'])

    def test_invalid_batch_is_noop(self):
        before = self.snapshot()
        for ids in ([], [self.a, self.a], [True], ['1'], list(range(1, 102))):
            with self.subTest(ids=ids):
                self.assertEqual(400, self.call('POST', '/issues/bulk', {
                    'ids': ids, 'changes': {'title': 'No'}}).status)
        self.assertEqual(before, self.snapshot())

    def test_tenant_fields_cannot_be_patched(self):
        self.assertEqual(400, self.call('PATCH', '/issues/' + str(self.a), {'tenant_id': 2}).status)
