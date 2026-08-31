import sqlite3
import tempfile
import unittest
from pathlib import Path

from issuehub import App, RequestContext

from support import TenantCase


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'legacy.sqlite'
        connection = sqlite3.connect(str(self.path))
        connection.executescript(Path(__file__).with_name('legacy_v1.sql').read_text())
        connection.close()

    def open_app(self):
        app = App(self.path)
        self.addCleanup(app.close)
        return app

    def test_upgrade_preserves_ids_comments_and_audit(self):
        app = self.open_app()
        self.assertEqual(2, app.db.connection.execute('PRAGMA user_version').fetchone()[0])
        context = RequestContext(1, 1)
        self.assertEqual('Legacy issue', app.service.get_issue(context, 30)['title'])
        self.assertEqual(50, app.service.list_comments(context, 30)[0]['id'])
        self.assertEqual(80, app.service.list_audit(context)[0]['id'])
        self.assertEqual([], app.db.connection.execute('PRAGMA foreign_key_check').fetchall())

    def test_old_queued_export_resumes_and_is_scoped(self):
        app = self.open_app()
        self.assertEqual(60, app.exports.run_next()['id'])
        content = app.exports.download(RequestContext(1, 1), 60)
        self.assertIn('Legacy issue', content)
        self.assertNotIn('Foreign legacy issue', content)

    def test_untrusted_old_ready_bytes_are_requeued_not_served(self):
        app = self.open_app()
        response = app.request('GET', '/exports/70/download', actor_id=1, tenant_id=1)
        self.assertEqual(409, response.status)
        row = app.db.connection.execute('SELECT state,content FROM export_jobs WHERE id=70').fetchone()
        self.assertEqual(('queued', None), tuple(row))
        app.exports.run_next()
        app.exports.run_next()
        self.assertNotIn('LEGACY UNSCOPED SECRET', app.exports.download(RequestContext(1, 1), 70))

    def test_upgrade_preserves_deleted_id_high_water(self):
        app = self.open_app()
        issue = app.service.create_issue(RequestContext(1, 1), 10, 'New after upgrade')
        self.assertGreater(issue['id'], 200)

    def test_reopening_v2_is_idempotent_and_does_not_requeue_fresh_ready_jobs(self):
        app = App(self.path)
        app.exports.run_next()
        app.close()
        second = self.open_app()
        self.assertEqual(2, second.db.connection.execute('PRAGMA user_version').fetchone()[0])
        self.assertEqual('ready', second.exports.get(RequestContext(1, 1), 60)['state'])

    def test_inconsistent_legacy_relation_fails_atomically(self):
        connection = sqlite3.connect(str(self.path))
        connection.execute('UPDATE export_jobs SET project_id=20 WHERE id=60')
        connection.commit()
        original = connection.execute('SELECT type,name,sql FROM sqlite_master ORDER BY type,name').fetchall()
        connection.close()
        with self.assertRaises(sqlite3.IntegrityError):
            failed = App(self.path)
            failed.close()
        connection = sqlite3.connect(str(self.path))
        try:
            self.assertEqual(1, connection.execute('PRAGMA user_version').fetchone()[0])
            self.assertEqual(original, connection.execute('SELECT type,name,sql FROM sqlite_master ORDER BY type,name').fetchall())
            self.assertEqual('Legacy issue', connection.execute('SELECT title FROM issues WHERE id=30').fetchone()[0])
        finally:
            connection.close()


class StorageInvariantTests(TenantCase):
    def test_issue_tenant_parent_constraint(self):
        columns = [row['name'] for row in self.app.db.connection.execute('PRAGMA table_info(issues)')]
        self.assertIn('tenant_id', columns)
        with self.assertRaises(sqlite3.IntegrityError):
            self.app.db.connection.execute('UPDATE issues SET project_id=? WHERE id=?', (self.pb, self.a))

    def test_comment_tenant_parent_constraint(self):
        columns = [row['name'] for row in self.app.db.connection.execute('PRAGMA table_info(comments)')]
        self.assertIn('tenant_id', columns)
        with self.assertRaises(sqlite3.IntegrityError):
            self.app.db.connection.execute(
                'INSERT INTO comments(tenant_id,issue_id,author_id,text) VALUES(1,?,1,?)',
                (self.b, 'Invalid relation'),
            )

    def test_export_filter_tenant_constraint(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.app.db.connection.execute(
                "INSERT INTO export_jobs(tenant_id,requested_by,project_id,state) VALUES(1,1,?,'queued')",
                (self.pb,),
            )

    def test_indexes_have_tenant_leading_lookup_paths(self):
        for table in ('issues', 'comments', 'export_jobs', 'audit'):
            with self.subTest(table=table):
                paths = []
                for row in self.app.db.connection.execute('PRAGMA index_list(' + table + ')'):
                    escaped = row['name'].replace('"', '""')
                    paths.append([column['name'] for column in self.app.db.connection.execute(
                        'PRAGMA index_info("' + escaped + '")')])
                self.assertTrue(any(path and path[0] == 'tenant_id' for path in paths), paths)
