from __future__ import annotations

from dandy import BaseIntel


class CollectionIntel(BaseIntel):
    name: str
    collection_id: int = None
