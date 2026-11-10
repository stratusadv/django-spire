from __future__ import annotations

from html.parser import HTMLParser

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

    def test_browse_toggle_can_hide(self):
        """Bootstrap's d-flex is !important, so an x-show beside it can never apply display: none."""
        response = self.client.get(reverse('django_spire:metric:report:page:report'))

        class BrowseToggleClasses(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.classes: list[str] = []

            def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
                attributes = dict(attrs)
                if attributes.get('x-show') == 'Spire.ui.hasContent($refs.full_page_sub_navigation)':
                    self.classes.append(attributes.get('class') or '')

        parser = BrowseToggleClasses()
        parser.feed(response.content.decode())
        assert len(parser.classes) == 1
        assert 'd-flex' not in parser.classes[0].split()
