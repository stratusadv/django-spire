from __future__ import annotations

from dandy import BaseIntel, BaseListIntel

from django_spire.knowledge.intelligence.intel.collection_intel import CollectionIntel


class EntryIntel(BaseIntel):
    body: str
    collection_intel: CollectionIntel


class EntriesIntel(BaseListIntel[EntryIntel]):
    entry_intel_list: list[EntryIntel]
