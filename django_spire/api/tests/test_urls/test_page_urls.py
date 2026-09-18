from __future__ import annotations

from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.core.tests.test_cases import BaseTestCase


class ApiPageUrlsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_access = ApiAccess.objects.create(name='Test Access')

    def test_access_list_view_url_path(self):
        response = self.client.get(path=reverse('django_spire:api:page:list'))
        assert response.status_code == 200

    def test_detail_url(self) -> None:
        url = reverse('django_spire:api:page:detail', kwargs={'pk': self.test_access.pk})
        response = self.client.get(url)

        assert response.status_code == 200

    def test_detail_url_pattern(self) -> None:
        url = reverse('django_spire:api:page:detail', kwargs={'pk': 123})

        assert url == '/ds/api/page/123/detail/'
