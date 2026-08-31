CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE tenants(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE memberships(
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    role TEXT NOT NULL CHECK(role IN ('viewer','editor','admin')),
    active INTEGER NOT NULL DEFAULT 1 CHECK(active IN (0,1)),
    PRIMARY KEY(tenant_id,user_id)
);
CREATE TABLE projects(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    name TEXT NOT NULL
);
CREATE TABLE issues(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('open','closed')),
    created_by INTEGER NOT NULL REFERENCES users(id)
);
CREATE TABLE comments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL REFERENCES issues(id),
    author_id INTEGER NOT NULL REFERENCES users(id),
    text TEXT NOT NULL
);
CREATE TABLE export_jobs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    requested_by INTEGER NOT NULL REFERENCES users(id),
    project_id INTEGER REFERENCES projects(id),
    state TEXT NOT NULL CHECK(state IN ('queued','ready','denied')),
    content TEXT,
    error TEXT
);
CREATE TABLE audit(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL REFERENCES tenants(id),
    actor_id INTEGER NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    resource_id INTEGER,
    details TEXT NOT NULL
);
CREATE INDEX issues_project_status ON issues(project_id,status,id);
PRAGMA user_version=1;

INSERT INTO users(id,name) VALUES(1,'Synthetic Admin'),(2,'Synthetic Other');
INSERT INTO tenants(id,name) VALUES(1,'Atlas'),(2,'Boreal');
INSERT INTO memberships VALUES(1,1,'admin',1),(2,2,'admin',1);
INSERT INTO projects(id,tenant_id,name) VALUES(10,1,'Original'),(20,2,'Foreign');
INSERT INTO issues(id,project_id,title,status,created_by)
VALUES(30,10,'Legacy issue','open',1),(40,20,'Foreign legacy issue','open',2);
INSERT INTO issues(id,project_id,title,status,created_by) VALUES(200,10,'Deleted high water','open',1);
DELETE FROM issues WHERE id=200;
INSERT INTO comments(id,issue_id,author_id,text) VALUES(50,30,1,'Original comment');
INSERT INTO export_jobs(id,tenant_id,requested_by,project_id,state) VALUES(60,1,1,NULL,'queued');
INSERT INTO export_jobs(id,tenant_id,requested_by,project_id,state,content)
VALUES(70,1,1,NULL,'ready','LEGACY UNSCOPED SECRET');
INSERT INTO audit(id,tenant_id,actor_id,action,resource_id,details)
VALUES(80,1,1,'issue.created',30,'{}');
