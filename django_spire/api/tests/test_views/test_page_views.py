from __future__ import annotations

from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.core.tests.test_cases import BaseTestCase


class ApiPageViewsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_access = ApiAccess.objects.create(name='Test Access')

    def test_access_list_view(self):
        response = self.client.get(path=reverse('django_spire:api:page:list'))
        assert response.status_code == 200
        self.assertTemplateUsed(response, 'django_spire/api/page/access_list_page.html')
        assert self.test_access in response.context['api_accesses']

    def test_access_list_view_shows_user_and_no_user(self):
        linked_access = ApiAccess.objects.create(name='Linked Access', user=self.super_user)
        html = self.client.get(path=reverse('django_spire:api:page:list')).content.decode()

        assert str(linked_access.user) in html
        assert 'No User' in html

    def test_detail_view_returns_200(self) -> None:
        url = reverse('django_spire:api:page:detail', kwargs={'pk': self.test_access.pk})
        response = self.client.get(url)

        assert response.status_code == 200

    def test_detail_view_contains_environment(self) -> None:
        url = reverse('django_spire:api:page:detail', kwargs={'pk': self.test_access.pk})
        response = self.client.get(url)

        assert 'api_access' in response.context
        assert response.context['api_access'].pk == self.test_access.pk

    def test_detail_view_returns_404_for_nonexistent_environment(self) -> None:
        url = reverse('django_spire:api:page:detail', kwargs={'pk': 99999})
        response = self.client.get(url)

        assert response.status_code == 404
