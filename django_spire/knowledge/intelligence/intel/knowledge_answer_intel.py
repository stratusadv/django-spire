from dandy import BaseIntel

from django_spire.knowledge.intelligence.intel.entry_intel import EntriesIntel


class KnowledgeAnswerIntel(BaseIntel):
    answer: str
    entries_intel: EntriesIntel
