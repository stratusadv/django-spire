from typing import List

from dandy.intel import BaseIntel, BaseListIntel

from django_spire.knowledge.intelligence.intel.collection_intel import CollectionIntel


class EntryIntel(BaseIntel):
    collection_intel: CollectionIntel


class EntriesIntel(BaseListIntel[EntryIntel]):
    entry_intel_list: List[EntryIntel]