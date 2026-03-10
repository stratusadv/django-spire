from __future__ import annotations

from django_spire.api.tools import hash_string
from django_spire.history.querysets import HistoryQuerySet


class ApiAccessQuerySet(HistoryQuerySet):
    def is_valid_key(self, key: str) -> bool:
        return self.active().filter(hashed_key=hash_string(key)).exists()

    def get_by_key_or_none(self, key: str) -> ApiAccessQuerySet | None:
        return self.active().filter(hashed_key=hash_string(key)).first()
