"""Run a deterministic end-to-end example with python -m issuehub."""

import json

from .api import App
from .seed import seed_demo


def main():
    app = App()
    try:
        seed_demo(app)
        print(json.dumps(app.request("GET", "/issues", actor_id=1, tenant_id=1).body, indent=2))
        job = app.request("POST", "/exports", actor_id=1, tenant_id=1).body
        app.exports.run_next()
        print(app.request("GET", "/exports/{}/download".format(job["id"]),
                          actor_id=1, tenant_id=1).body, end="")
    finally:
        app.close()


if __name__ == "__main__":
    main()
