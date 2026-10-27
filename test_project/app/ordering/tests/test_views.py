from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from test_project.app.ordering.tests.factories import create_test_duck


class DuckFormViewTestCase(BaseTestCase):
    def test_saving_an_edit_returns_to_the_return_url(self) -> None:
        duck = create_test_duck(name='Mallard')
        component_url = reverse('order:list_component')

        response = self.client.post(
            f"{reverse('order:update', kwargs={'pk': duck.pk})}?return_url={component_url}",
            {'name': 'Teal', 'color': '#336699'},
        )

        duck.refresh_from_db()

        assert response.status_code == 302
        assert response.url == component_url
        assert duck.name == 'Teal'

    def test_saving_a_new_duck_returns_to_the_return_url(self) -> None:
        component_url = reverse('order:list_component')

        response = self.client.post(
            f"{reverse('order:create')}?return_url={component_url}",
            {'name': 'Teal', 'color': '#336699'},
        )

        assert response.status_code == 302
        assert response.url == component_url

    def test_without_a_return_url_saving_returns_to_the_ordering_page(self) -> None:
        duck = create_test_duck()

        response = self.client.post(
            reverse('order:update', kwargs={'pk': duck.pk}),
            {'name': 'Teal', 'color': '#336699'},
        )

        assert response.status_code == 302
        assert response.url == reverse('order:list')
