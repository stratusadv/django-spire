from __future__ import annotations

from functools import reduce
from operator import or_
from typing import TYPE_CHECKING

from django.contrib.postgres.search import SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import F, Q, Value
from django.db.models.functions import Coalesce

from django_spire.contrib.service import BaseDjangoModelService
from django_spire.knowledge.intelligence.workflows.search_preprocessing_workflow import preprocess_search_query

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from django_spire.knowledge.entry.models import Entry


class EntrySearchService(BaseDjangoModelService['Entry']):
    obj: Entry

    def search(
        self,
        query: str,
        use_llm_preprocessing: bool = True,
    ) -> QuerySet[Entry]:
        query = query.strip() if query else ''

        if not query:
            return self.obj_class.objects.none()

        if use_llm_preprocessing:
            preprocessed = preprocess_search_query(query=query)
            primary_query = preprocessed.primary_search_query
            all_terms = preprocessed.all_search_terms
        else:
            primary_query = query
            all_terms = set(query.split())

        if not primary_query:
            return self.obj_class.objects.none()

        search_query = SearchQuery(primary_query, search_type='websearch', config='english')

        word_filters = []

        for word in all_terms:
            if len(word) >= 2:
                word_filters.append(Q(name__icontains=word))
                word_filters.append(Q(_search_text__icontains=word))

        combined_word_filter = reduce(or_, word_filters) if word_filters else Q()

        return (
            self.obj_class.objects
            .active()
            .has_current_version()
            .annotate(
                vector_rank=Coalesce(
                    SearchRank(F('_search_vector'), search_query),
                    Value(0.0)
                ),
                name_similarity=TrigramSimilarity('name', primary_query),
                combined_score=(
                    F('vector_rank') * 2.0 +
                    F('name_similarity') * 1.5
                )
            )
            .filter(
                Q(vector_rank__gt=0.01) |
                Q(name_similarity__gt=0.2) |
                combined_word_filter
            )
            .order_by('-combined_score', '-id')
            .distinct()
        )
