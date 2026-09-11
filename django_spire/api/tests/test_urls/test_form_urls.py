from __future__ import annotations

from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.core.tests.test_cases import BaseTestCase


class ApiFormUrlsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_access = ApiAccess.objects.create(name='Test Access')

    def test_access_create_form_view_url_path(self):
        response = self.client.get(path=reverse('django_spire:api:form:create'))
        assert response.status_code == 200

    def test_access_delete_view_url_path(self):
        response = self.client.get(
            path=reverse('django_spire:api:form:delete', kwargs={'pk': self.test_access.pk})
        )
        assert response.status_code == 200
