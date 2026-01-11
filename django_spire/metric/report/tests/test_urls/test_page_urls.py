from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase


class ReportPageUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_report_view_url_path(self):
        response = self.client.get(
            reverse('django_spire:metric:report:page:report')
        )
        assert response.status_code == 200
