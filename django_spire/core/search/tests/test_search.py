from __future__ import annotations

import pytest
from django.test import TestCase

from django_spire.core.search.result import SearchResult
from django_spire.core.search.search import BaseSearch
from test_project.app.task import models
from test_project.app.task.search import TaskSearch


class TestTaskSearch(TestCase):
    def setUp(self) -> None:
        self.search = TaskSearch()
        self.matching_name = models.Task.objects.create(name='Alpha Report', description='first')
        self.matching_description = models.Task.objects.create(
            name='Beta', description='report details'
        )
        self.other = models.Task.objects.create(name='Gamma', description='third')
        self.deleted = models.Task.objects.create(name='Delta Report', description='fourth')
        self.deleted.set_deleted()

    def test_search_matches_name(self) -> None:
        results = self.search.search('Alpha')
        assert set(results.values_list('pk', flat=True)) == {self.matching_name.pk}

    def test_search_matches_description(self) -> None:
        results = self.search.search('details')
        assert set(results.values_list('pk', flat=True)) == {self.matching_description.pk}

    def test_search_matches_multiple_words_across_fields(self) -> None:
        results = self.search.search('first report')
        assert set(results.values_list('pk', flat=True)) == {self.matching_name.pk}

    def test_search_multiple_words_must_match_same_row(self) -> None:
        results = self.search.search('report details')
        assert set(results.values_list('pk', flat=True)) == {self.matching_description.pk}

    def test_search_excludes_deleted(self) -> None:
        results = self.search.search('Delta')
        assert results is not None
        assert not results.exists()

    def test_search_blank_returns_none(self) -> None:
        assert self.search.search(None) is None
        assert self.search.search('   ') is None

    def test_search_no_match_returns_empty(self) -> None:
        assert not self.search.search('zzzzzzz').exists()

    def test_to_result(self) -> None:
        result = self.search.to_result(self.matching_name)

        assert result.search_key == 'TASK'
        assert result.name == 'Tasks'
        assert result.icon == 'bi-list-task'
        assert result.label == 'Alpha Report'
        assert result.description is None
        assert result.url == f'/task/page/detail/{self.matching_name.pk}/'

    def test_result_from_search(self) -> None:
        result = SearchResult.from_search(self.search, self.matching_name)

        assert result.search_key == 'TASK'
        assert result.name == 'Tasks'
        assert result.label == 'Alpha Report'
        assert result.url == f'/task/page/detail/{self.matching_name.pk}/'

    def test_section_name(self) -> None:
        assert self.search.section_name == 'Tasks'

    def test_result_limit(self) -> None:
        for index in range(12):
            models.Task.objects.create(name=f'Bulk Report {index}', description='bulk')

        results = self.search.search('Bulk')
        assert len(list(results)) == self.search.result_limit


class TestBaseSearchValidation(TestCase):
    def test_missing_model_class_raises(self) -> None:
        with pytest.raises(ValueError, match='model_class is None and must be defined'):

            class InvalidSearch(BaseSearch):
                searchable_fields = ['name']
                search_key = 'INVALID'

                def generate_url(self, _obj: models.Task) -> str:
                    return ''

    def test_missing_searchable_fields_raises(self) -> None:
        with pytest.raises(ValueError, match='searchable_fields is None and must be defined'):

            class InvalidSearch(BaseSearch):
                model_class = models.Task
                search_key = 'INVALID'

                def generate_url(self, _obj: models.Task) -> str:
                    return ''

    def test_missing_search_key_raises(self) -> None:
        with pytest.raises(ValueError, match='search_key is None and must be defined'):

            class InvalidSearch(BaseSearch):
                model_class = models.Task
                searchable_fields = ['name']

                def generate_url(self, _obj: models.Task) -> str:
                    return ''
