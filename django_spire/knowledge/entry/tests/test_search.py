from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from django_spire.knowledge.entry.search import EntrySearch
from django_spire.knowledge.entry.tests.factories import create_test_collection, create_test_entry


class TestEntrySearch(TestCase):
    def setUp(self) -> None:
        self.search = EntrySearch()
        self.collection = create_test_collection(name='Guides')
        self.matching_name = create_test_entry(
            collection=self.collection, name='Installation Guide', _search_text='setup basics'
        )
        self.matching_text = create_test_entry(
            collection=self.collection, name='Troubleshooting', _search_text='known issues database'
        )
        self.other = create_test_entry(collection=self.collection, name='Basics')
        self.deleted = create_test_entry(collection=self.collection, name='Archive Guide')
        self.deleted.set_deleted()

    def test_search_matches_name(self) -> None:
        results = self.search.search('Guide')
        assert set(results.values_list('pk', flat=True)) == {self.matching_name.pk}

    def test_search_matches_search_text(self) -> None:
        results = self.search.search('database')
        assert set(results.values_list('pk', flat=True)) == {self.matching_text.pk}

    def test_search_matches_multiple_words_across_fields(self) -> None:
        results = self.search.search('installation basics')
        assert set(results.values_list('pk', flat=True)) == {self.matching_name.pk}

    def test_search_excludes_deleted(self) -> None:
        results = self.search.search('Archive')
        assert results is not None
        assert not results.exists()

    def test_search_blank_returns_none(self) -> None:
        assert self.search.search(None) is None
        assert self.search.search('   ') is None

    def test_to_result(self) -> None:
        result = self.search.to_result(self.matching_name)

        assert result.search_key == 'ENTRY'
        assert result.name == 'Knowledge Entries'
        assert result.icon == 'bi-book'
        assert result.label == 'Installation Guide'
        assert result.description == 'Guides'
        assert result.url == reverse(
            'django_spire:knowledge:entry:version:page:editor', kwargs={'pk': self.matching_name.pk}
        )

    def test_to_result_prefetches_collection(self) -> None:
        entry = next(iter(self.search.search('Guide')))

        with self.assertNumQueries(0):
            result = self.search.to_result(entry)

        assert result.description == 'Guides'

    def test_list_url(self) -> None:
        assert self.search.generate_list_url() == reverse('django_spire:knowledge:page:home')

    def test_list_result_matches_section_keyword(self) -> None:
        result = self.search.list_result('knowledge')

        assert result is not None
        assert result.label == 'Knowledge Entries'
        assert result.url == reverse('django_spire:knowledge:page:home')

    def test_list_result_none_for_unrelated_query(self) -> None:
        assert self.search.list_result('guide') is None
