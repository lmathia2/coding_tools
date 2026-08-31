"""Process-local JSON-shaped response cache with caller isolation by copying."""

from copy import deepcopy


class QueryCache:
    def __init__(self):
        self._values = {}

    def get(self, tenant_id, kind, key):
        return deepcopy(self._values.get((tenant_id, kind, key)))

    def put(self, tenant_id, kind, key, value):
        self._values[(tenant_id, kind, key)] = deepcopy(value)

    def invalidate(self, tenant_id):
        self._values = {key: value for key, value in self._values.items()
                        if key[0] != tenant_id}
