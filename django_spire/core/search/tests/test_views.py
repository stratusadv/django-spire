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

    def test_search_palette_requires_login(self) -> None:
        self.client.logout()

        response = self.client.get(reverse('django_spire:core:search:search_palette'))

        assert response.status_code == 302

    def test_search_palette_renders_sections(self) -> None:
        response = self.client.get(reverse('django_spire:core:search:search_palette'))

        assert response.status_code == 200
        self.assertContains(response, 'searchPalette')
        self.assertContains(response, 'Searchable Areas')
        self.assertContains(response, 'Tasks')

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

    def test_search_results_blank_query_returns_sections(self) -> None:
        response = self.client.get(reverse('django_spire:core:search:results'))

        assert response.status_code == 200
        self.assertContains(response, 'Searchable Areas')


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
