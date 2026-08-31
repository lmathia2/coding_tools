"""Process-local JSON-shaped response cache with caller isolation by copying."""

from copy import deepcopy


class QueryCache:
    def __init__(self):
        self._values = {}

    def get(self, tenant_id, kind, key):
        return deepcopy(self._values.get((kind, key)))

    def put(self, tenant_id, kind, key, value):
        self._values[(kind, key)] = deepcopy(value)

    def invalidate(self, tenant_id):
        self._values.clear()
