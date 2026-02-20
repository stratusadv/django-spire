from __future__ import annotations

import hashlib

from dataclasses import dataclass

from django.core.cache import cache

from django_spire.knowledge.intelligence.bots.search_preprocessing_bot import (
    PreprocessedQueryIntel,
    SearchPreprocessingBot,
)


PREPROCESSING_CACHE_TIMEOUT = 3600


def _get_cache_key(query: str) -> str:
    normalized = query.lower().strip()
    query_hash = hashlib.sha256(normalized.encode()).hexdigest()
    return f'knowledge_search_preprocess:{query_hash}'


@dataclass
class PreprocessedSearchQuery:
    corrected_query: str
    expanded_terms: list[str]
    meaningful_words: list[str]
    original_query: str
    search_phrases: list[str]

    @property
    def all_search_terms(self) -> set[str]:
        terms = set(self.meaningful_words)
        terms.update(self.expanded_terms)

        if not terms:
            terms.add(self.corrected_query or self.original_query)

        return terms

    @property
    def primary_search_query(self) -> str:
        if self.meaningful_words:
            return ' '.join(self.meaningful_words)

        return self.corrected_query or self.original_query


def preprocess_search_query(
    query: str,
    use_cache: bool = True,
    llm_temperature: float = 0.3
) -> PreprocessedSearchQuery:
    if use_cache:
        cache_key = _get_cache_key(query)
        cached = cache.get(cache_key)

        if cached:
            return cached

    search_bot = SearchPreprocessingBot()

    search_bot.llm.options.temperature = llm_temperature

    intel: PreprocessedQueryIntel = (
        search_bot
        .process(query=query)
    )

    result = PreprocessedSearchQuery(
        corrected_query=intel.corrected_query,
        expanded_terms=intel.expanded_terms,
        meaningful_words=intel.meaningful_words,
        original_query=query,
        search_phrases=intel.search_phrases,
    )

    if use_cache:
        cache.set(cache_key, result, PREPROCESSING_CACHE_TIMEOUT)

    return result
