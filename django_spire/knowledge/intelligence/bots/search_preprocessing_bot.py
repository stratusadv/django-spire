from __future__ import annotations

from dandy import BaseIntel, Bot, Prompt


class PreprocessedQueryIntel(BaseIntel):
    corrected_query: str
    meaningful_words: list[str]
    expanded_terms: list[str]
    search_phrases: list[str]


class SearchPreprocessingBot(Bot):
    intel_class = PreprocessedQueryIntel
    role = 'Search Query Preprocessor'
    task = 'Process a user search query to optimize it for knowledge base retrieval.'
    guidelines = (
        Prompt()
        .list([
            'Correct any obvious spelling or grammar mistakes while preserving intent.',
            'Identify meaningful words by removing stop words (the, a, an, is, are, how, what, can, do, etc.).',
            'Keep technical terms, acronyms, nouns, verbs, and domain-specific vocabulary as meaningful words.',
            'Generate 3-5 synonyms or related terms for key concepts in expanded_terms.',
            'Provide 2-3 alternative search phrases in search_phrases.',
            'Do not change proper nouns or technical terminology.',
        ])
    )

    def process(self, query: str) -> PreprocessedQueryIntel:
        return self.llm.prompt_to_intel(
            prompt=f'Process this search query: {query}'
        )
