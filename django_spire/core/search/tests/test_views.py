from __future__ import annotations

from django.test import override_settings
from django.urls import reverse

from django_spire.auth.user.models import AuthUser
from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.task import models
from test_project.app.task.search import TaskSearch


class PermissionedTaskSearch(TaskSearch):
    permission = 'test_project.view_task'


SEARCH_REGISTRY = {'TASK': 'test_project.app.task.search.TaskSearch'}


@override_settings(DJANGO_SPIRE_SEARCH_REGISTRY=SEARCH_REGISTRY)
class TestSearchPaletteViews(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.task = models.Task.objects.create(name='Searchable Widget', description='details')
        models.TaskUser.objects.create(user=self.super_user, task=self.task)

    def test_search_palette_requires_login(self) -> None:
        self.client.logout()

        response = self.client.get(reverse('django_spire:core:search:search_palette'))

        assert response.status_code == 302

    def test_search_palette_renders_sections(self) -> None:
        response = self.client.get(reverse('django_spire:core:search:search_palette'))

        assert response.status_code == 200
        self.assertContains(response, 'searchPalette')
        self.assertContains(response, 'Nothing to show')

    def test_search_palette_renders_results_for_query(self) -> None:
        response = self.client.get(
            reverse('django_spire:core:search:search_palette'), {'q': 'Searchable'}
        )

        assert response.status_code == 200
        self.assertContains(response, 'Searchable Widget')
        self.assertContains(response, reverse('task:page:detail', kwargs={'pk': self.task.pk}))

    def test_search_results_returns_matches(self) -> None:
        response = self.client.get(reverse('django_spire:core:search:results'), {'q': 'Searchable'})

        assert response.status_code == 200
        self.assertContains(response, 'Searchable Widget')
        self.assertContains(response, reverse('task:page:detail', kwargs={'pk': self.task.pk}))

    def test_search_results_renders_list_page_for_section_query(self) -> None:
        response = self.client.get(reverse('django_spire:core:search:results'), {'q': 'task'})

        assert response.status_code == 200
        self.assertContains(response, reverse('task:page:list'))
        self.assertContains(response, 'New Task')

    def test_search_results_blank_query_returns_sections(self) -> None:
        response = self.client.get(reverse('django_spire:core:search:results'))

        assert response.status_code == 200
        self.assertContains(response, 'Nothing to show')


@override_settings(DJANGO_SPIRE_SEARCH_REGISTRY=SEARCH_REGISTRY)
class TestSearchPaletteCommands(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.task = models.Task.objects.create(name='Searchable Widget', description='details')
        models.TaskUser.objects.create(user=self.super_user, task=self.task)

    def test_command_result_shown_for_command_query(self) -> None:
        response = self.client.get(reverse('django_spire:core:search:results'), {'q': 'new'})

        assert response.status_code == 200
        self.assertContains(response, 'New Task')
        self.assertContains(response, '/task/modal/0/form/')

    def test_command_not_shown_for_unrelated_query(self) -> None:
        response = self.client.get(reverse('django_spire:core:search:results'), {'q': 'Searchable'})

        assert response.status_code == 200
        self.assertNotContains(response, 'New Task')
        self.assertContains(response, 'Searchable Widget')


@override_settings(DJANGO_SPIRE_SEARCH_REGISTRY=SEARCH_REGISTRY)
class TestSearchPaletteCommandPermissions(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = AuthUser.objects.create_user(username='search_command_user')

    def test_command_hidden_without_permission(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(reverse('django_spire:core:search:results'), {'q': 'new'})

        assert response.status_code == 200
        self.assertNotContains(response, 'New Task')


@override_settings(
    DJANGO_SPIRE_SEARCH_REGISTRY={
        'TASK': 'django_spire.core.search.tests.test_views.PermissionedTaskSearch'
    }
)
class TestSearchPalettePermissions(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.user = AuthUser.objects.create_user(username='search_palette_user')

    def test_search_excluded_without_permission(self) -> None:
        self.client.force_login(self.user)

        response = self.client.get(reverse('django_spire:core:search:search_palette'))

        assert response.status_code == 200
        self.assertNotContains(response, 'Tasks')
