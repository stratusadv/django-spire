from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase


class ApiFormUrlsTestCase(BaseTestCase):
    def test_access_create_form_view_url_path(self):
        response = self.client.get(path=reverse('django_spire:api:form:create'))
        assert response.status_code == 200
