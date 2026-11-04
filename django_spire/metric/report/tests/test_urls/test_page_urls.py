from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase


class ReportPageUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_report_view_url_path(self):
        response = self.client.get(reverse('django_spire:metric:report:page:report'))
        assert response.status_code == 200

    def test_browse_toggle_uses_spire_has_content(self):
        """The global has_content() was removed; calling it throws on every report page."""
        response = self.client.get(reverse('django_spire:metric:report:page:report'))
        content = response.content.decode()
        assert 'Spire.ui.hasContent($refs.full_page_sub_navigation)' in content
        assert 'x-show="has_content(' not in content
