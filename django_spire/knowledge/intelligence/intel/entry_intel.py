from __future__ import annotations

from dandy import BaseIntel, BaseListIntel

from django_spire.knowledge.intelligence.intel.collection_intel import CollectionIntel


class EntryIntel(BaseIntel):
    relevant_heading_text: str
    relevant_subject_text: str
    relevant_block_id: int
    entry_id: int = None
    collection_intel: CollectionIntel = None


class EntriesIntel(BaseListIntel[EntryIntel]):
    entry_intel_list: list[EntryIntel]
