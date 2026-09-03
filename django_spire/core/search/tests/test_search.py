from __future__ import annotations

import pytest
from django.test import RequestFactory, TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.core.search.result import SearchResult
from django_spire.core.search.search import Search
from test_project.app.task import models
from test_project.app.task.search import TaskSearch


class TestTaskSearch(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.search = TaskSearch()
        self.user = AuthUser.objects.create_user(username='searchuser')
        self.request = RequestFactory().get('/')
        self.request.user = self.user

        self.matching_name = self._create_task('Alpha Report', 'first')
        self.matching_description = self._create_task('Beta', 'report details')
        self.other = self._create_task('Gamma', 'third')
        self.deleted = self._create_task('Delta Report', 'fourth')
        self.deleted.set_deleted()

    def _create_task(self, name: str, description: str) -> models.Task:
        task = models.Task.objects.create(name=name, description=description)
        models.TaskUser.objects.create(user=self.user, task=task)
        return task

    def test_search_matches_name(self) -> None:
        results = self.search.search(self.request, 'Alpha')
        assert set(results.values_list('pk', flat=True)) == {self.matching_name.pk}

    def test_search_matches_description(self) -> None:
        results = self.search.search(self.request, 'details')
        assert set(results.values_list('pk', flat=True)) == {self.matching_description.pk}

    def test_search_matches_multiple_words_across_fields(self) -> None:
        results = self.search.search(self.request, 'first report')
        assert set(results.values_list('pk', flat=True)) == {self.matching_name.pk}

    def test_search_multiple_words_must_match_same_row(self) -> None:
        results = self.search.search(self.request, 'report details')
        assert set(results.values_list('pk', flat=True)) == {self.matching_description.pk}

    def test_search_excludes_deleted(self) -> None:
        results = self.search.search(self.request, 'Delta')
        assert results is not None
        assert not results.exists()

    def test_search_blank_returns_none(self) -> None:
        assert self.search.search(self.request, None) is None
        assert self.search.search(self.request, '   ') is None

    def test_search_no_match_returns_empty(self) -> None:
        assert not self.search.search(self.request, 'zzzzzzz').exists()

    def test_search_only_returns_tasks_for_request_user(self) -> None:
        other_user = AuthUser.objects.create_user(username='otheruser')
        other_task = models.Task.objects.create(name='Alpha Other', description='first')
        models.TaskUser.objects.create(user=other_user, task=other_task)

        results = self.search.search(self.request, 'Alpha')
        assert set(results.values_list('pk', flat=True)) == {self.matching_name.pk}

        other_request = RequestFactory().get('/')
        other_request.user = other_user
        other_results = self.search.search(other_request, 'Alpha')
        assert set(other_results.values_list('pk', flat=True)) == {other_task.pk}

    def test_to_result(self) -> None:
        result = self.search.to_result(self.matching_name)

        assert result.name == 'Tasks'
        assert result.icon == 'bi-list-task'
        assert result.label == 'Alpha Report'
        assert result.description == 'first'
        assert result.url == f'/task/page/detail/{self.matching_name.pk}/'

    def test_result_from_search(self) -> None:
        result = SearchResult.from_search(self.search, self.matching_name)

        assert result.name == 'Tasks'
        assert result.label == 'Alpha Report'
        assert result.description == 'first'
        assert result.url == f'/task/page/detail/{self.matching_name.pk}/'

    def test_section_name(self) -> None:
        assert self.search.section_name == 'Tasks'

    def test_result_limit(self) -> None:
        for index in range(12):
            self._create_task(f'Bulk Report {index}', 'bulk')

        results = self.search.search(self.request, 'Bulk')
        assert len(list(results)) == self.search.result_limit

    def test_searchable_commands_defined(self) -> None:
        assert [command.name for command in TaskSearch.searchable_commands] == ['New Task']

    def test_commands_for_query_matches_name(self) -> None:
        commands = self.search.commands_for_query('new')

        assert [command.name for command in commands] == ['New Task']

    def test_commands_for_query_matches_multi_word(self) -> None:
        commands = self.search.commands_for_query('new task')

        assert [command.name for command in commands] == ['New Task']

    def test_commands_for_query_no_match(self) -> None:
        assert self.search.commands_for_query('zzzz') == []

    def test_commands_for_query_blank_returns_empty(self) -> None:
        assert self.search.commands_for_query('') == []
        assert self.search.commands_for_query('   ') == []

    def test_command_url(self) -> None:
        command = TaskSearch.searchable_commands[0]

        assert command.url == '/task/modal/0/form/'
        assert command.description == 'Create a new task'

    def test_command_result(self) -> None:
        command = TaskSearch.searchable_commands[0]
        result = self.search.command_result(command)

        assert result.name == 'Tasks'
        assert result.icon == 'bi-plus-lg'
        assert result.label == 'New Task'
        assert result.description == 'Create a new task'
        assert result.url == '/task/modal/0/form/'

    def test_list_url(self) -> None:
        assert self.search.generate_list_url() == '/task/page/list/'

    def test_list_result_matches_section_keyword(self) -> None:
        result = self.search.list_result('task')

        assert result is not None
        assert result.label == 'Tasks'
        assert result.icon == 'bi-list-columns'
        assert result.url == '/task/page/list/'

    def test_list_result_matches_case_insensitive(self) -> None:
        assert self.search.list_result('Task') is not None
        assert self.search.list_result('TASKS') is not None
        assert self.search.list_result('task management') is None

    def test_list_result_none_for_unrelated_query(self) -> None:
        assert self.search.list_result('report') is None
        assert self.search.list_result('new') is None
        assert self.search.list_result('') is None
        assert self.search.list_result('   ') is None


class TestBaseSearchValidation(TestCase):
    def test_missing_name_raises(self) -> None:
        with pytest.raises(ValueError, match=r'InvalidSearch\.name is None and must be defined'):

            class InvalidSearch(Search):
                icon = 'bi-list-task'

                def generate_detail_url(self, _obj: models.Task) -> str:
                    return ''

    def test_missing_icon_raises(self) -> None:
        with pytest.raises(ValueError, match=r'InvalidSearch\.icon is None and must be defined'):

            class InvalidSearch(Search):
                name = 'Tasks'

                def generate_detail_url(self, _obj: models.Task) -> str:
                    return ''

    def test_optional_attributes_are_not_required(self) -> None:
        class OptionalSearch(Search):
            name = 'Tasks'
            icon = 'bi-list-task'

            def generate_detail_url(self, _obj: models.Task) -> str:
                return ''

        assert OptionalSearch.model_class is None
