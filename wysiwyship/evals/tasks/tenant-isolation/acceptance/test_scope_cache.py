from support import TenantCase


class ScopeAndCacheTests(TenantCase):
    def test_project_list_is_scoped(self):
        self.assertEqual([self.pa], [p['id'] for p in self.call('GET', '/projects').body])
        self.assertEqual([self.pb], [p['id'] for p in self.call('GET', '/projects', tenant=2).body])

    def test_list_and_search_cannot_return_foreign_rows(self):
        for query in ({}, {'q': 'shared'}, {'status': 'open'}, {'q': 'confidential', 'status': 'open'}):
            with self.subTest(query=query):
                self.assertEqual([self.a], [i['id'] for i in self.call('GET', '/issues', query=query).body])
                self.assertEqual([self.b], [i['id'] for i in self.call('GET', '/issues', tenant=2, query=query).body])

    def test_foreign_and_absent_detail_are_indistinguishable(self):
        foreign = self.call('GET', '/issues/' + str(self.b))
        absent = self.call('GET', '/issues/999999')
        self.assertMissing(foreign)
        self.assertEqual((absent.status, absent.body), (foreign.status, foreign.body))

    def test_foreign_and_absent_project_filters_are_indistinguishable(self):
        foreign = self.call('GET', '/issues', query={'project_id': self.pb})
        absent = self.call('GET', '/issues', query={'project_id': 999999})
        self.assertMissing(foreign)
        self.assertEqual((absent.status, absent.body), (foreign.status, foreign.body))

    def test_detail_cache_is_tenant_partitioned(self):
        self.assertEqual(200, self.call('GET', '/issues/' + str(self.b), tenant=2).status)
        self.assertMissing(self.call('GET', '/issues/' + str(self.b)))
        self.assertEqual(200, self.call('GET', '/issues/' + str(self.b), actor=2, tenant=2).status)

    def test_same_query_cache_can_alternate_tenants(self):
        for tenant, expected in ((1, self.a), (2, self.b), (1, self.a), (2, self.b)):
            with self.subTest(tenant=tenant):
                response = self.call('GET', '/issues', tenant=tenant, query={'q': 'shared'})
                self.assertEqual([expected], [row['id'] for row in response.body])

    def test_comments_require_scoped_parent_even_when_empty(self):
        self.assertMissing(self.call('GET', '/issues/' + str(self.b) + '/comments'))
        self.assertMissing(self.call('GET', '/issues/999999/comments'))
        self.assertEqual([], self.call('GET', '/issues/' + str(self.a) + '/comments').body)

    def test_create_and_patch_invalidate_all_affected_query_variants(self):
        self.call('GET', '/issues', query={'status': 'closed'})
        self.call('GET', '/issues', query={'q': 'new'})
        self.call('GET', '/issues/' + str(self.a))
        self.call('PATCH', '/issues/' + str(self.a), {'status': 'closed'})
        created = self.call('POST', '/issues', {'project_id': self.pa, 'title': 'new issue'}).body
        self.assertEqual([self.a], [i['id'] for i in self.call('GET', '/issues', query={'status': 'closed'}).body])
        self.assertEqual([created['id']], [i['id'] for i in self.call('GET', '/issues', query={'q': 'new'}).body])
        self.assertEqual('closed', self.call('GET', '/issues/' + str(self.a)).body['status'])

    def test_storage_repository_scope_is_independent_of_adapter(self):
        self.assertEqual([self.a], [row['id'] for row in self.app.repo.issues(1)])
        self.assertDomain(404, self.app.repo.issue, 1, self.b)
        self.assertDomain(404, self.app.repo.project, 1, self.pb)

    def test_cache_invalidates_only_requested_partition(self):
        self.app.cache.put(1, 'contract-probe', 'key', {'v': 1})
        self.app.cache.put(2, 'contract-probe', 'key', {'v': 2})
        self.call('PATCH', '/issues/' + str(self.a), {'title': 'Updated'})
        self.assertIsNone(self.app.cache.get(1, 'contract-probe', 'key'))
        self.assertEqual({'v': 2}, self.app.cache.get(2, 'contract-probe', 'key'))
