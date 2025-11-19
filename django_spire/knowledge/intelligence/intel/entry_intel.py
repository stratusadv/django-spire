from __future__ import annotations

from enum import Enum

from dandy import BaseIntel, BaseListIntel

from django_spire.knowledge.entry.models import Entry


class EntryRelevancy(str, Enum):
    EXTREMELY = 'Extremely'
    VERY = 'Very'
    SOMEWHAT = 'Somewhat'
    NOT_SO_MUCH = 'Not so much'
    NO_RELEVANCE = 'No Relevance'


class EntryIntel(BaseIntel):
    relevant_heading_text: str
    relevant_text: str
    relevant_block_id: int
    relevancy: EntryRelevancy

    def __str__(self):
        return self.relevant_heading_text + ' ' + self.relevant_text

    @property
    def collection(self):
        return self.entry.collection

    @property
    def entry(self):
        return Entry.objects.get_by_version_block_id(self.relevant_block_id)


class EntriesIntel(BaseListIntel[EntryIntel]):
    entry_intel_list: list[EntryIntel]
