"""Evaluator fixtures use the documented maintenance DB port, not private helpers."""

import unittest

from issuehub import App, RequestContext
from issuehub.errors import DomainError


NOT_FOUND = {'error': {'code': 'not_found', 'message': 'Resource not found'}}


class TenantCase(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.addCleanup(self.app.close)
        sql = self.app.db.connection
        with self.app.db.transaction():
            sql.executemany('INSERT INTO tenants(id,name) VALUES(?,?)', [(1, 'Atlas'), (2, 'Boreal')])
            sql.executemany('INSERT INTO users(id,name) VALUES(?,?)', [
                (1, 'A Admin/B Viewer'), (2, 'A Editor/B Admin'), (3, 'A Viewer'),
                (4, 'No membership'), (5, 'Another A Admin'),
            ])
            sql.executemany('INSERT INTO memberships(tenant_id,user_id,role) VALUES(?,?,?)', [
                (1, 1, 'admin'), (2, 1, 'viewer'), (1, 2, 'editor'),
                (2, 2, 'admin'), (1, 3, 'viewer'), (1, 5, 'admin'),
            ])
        self.pa = self.call('POST', '/projects', {'name': 'Atlas project'}).body['id']
        self.pb = self.call('POST', '/projects', {'name': 'Boreal project'}, actor=2, tenant=2).body['id']
        self.a = self.call('POST', '/issues', {'project_id': self.pa, 'title': 'shared Atlas confidential'}).body['id']
        self.b = self.call('POST', '/issues', {'project_id': self.pb, 'title': 'shared Boreal confidential'}, actor=2, tenant=2).body['id']

    def call(self, method, path, body=None, *, actor=1, tenant=1, query=None):
        return self.app.request(method, path, actor_id=actor, tenant_id=tenant, body=body, query=query)

    def change_membership(self, tenant, actor, *, role=None, active=None):
        if role is not None:
            self.app.db.connection.execute('UPDATE memberships SET role=? WHERE tenant_id=? AND user_id=?',
                                           (role, tenant, actor))
        if active is not None:
            self.app.db.connection.execute('UPDATE memberships SET active=? WHERE tenant_id=? AND user_id=?',
                                           (active, tenant, actor))

    def assertMissing(self, response):
        self.assertEqual(404, response.status)
        self.assertEqual(NOT_FOUND, response.body)

    def assertDomain(self, status, function, *args):
        with self.assertRaises(DomainError) as caught:
            function(*args)
        self.assertEqual(status, caught.exception.status)
        return caught.exception

    def snapshot(self):
        """Compare durable business state, allowing intentional denial audit."""
        return {table: [tuple(row) for row in self.app.db.connection.execute(
            'SELECT * FROM ' + table + ' ORDER BY id')]
                for table in ('projects', 'issues', 'comments', 'export_jobs')}
