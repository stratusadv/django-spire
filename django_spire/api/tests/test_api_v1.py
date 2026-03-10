from __future__ import annotations

from django.test import TestCase, Client
from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.api.choices import ApiPermissionChoices


class NinjaApiV1TestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.raw_key = 'ninja_test_key'
        self.access = ApiAccess.objects.create(name='Ninja Test', level=ApiPermissionChoices.CHANGE)
        self.access.set_key_and_save(self.raw_key)

    def test_api_v1_authenticated_success(self) -> None:
        # Use reverse to get the API URL and test the internal test router
        url = reverse('django_spire:api_v1:test') + '?value=hello'
        response = self.client.get(url, HTTP_API_KEY=self.raw_key)

        assert response.status_code == 200
        assert response.json() == 'Test API successfully called with "hello" as a value.'

    def test_api_v1_unauthenticated(self) -> None:
        url = reverse('django_spire:api_v1:test') + '?value=hello'
        response = self.client.get(url)

        assert response.status_code == 401

    def test_api_v1_insufficient_permissions(self) -> None:
        # Create a key with VIEW level
        low_access_key = 'low_access_key'
        low_access = ApiAccess.objects.create(name='Low Access', level=ApiPermissionChoices.VIEW)
        low_access.set_key_and_save(low_access_key)

        # /test/test requires CHANGE level (3), VIEW is (1)
        url = reverse('django_spire:api_v1:test') + '?value=hello'
        response = self.client.get(url, HTTP_API_KEY=low_access_key)

        assert response.status_code == 401  # Ninja returns 401 for auth failure
