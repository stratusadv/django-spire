from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from test_project.apps.infinite_scrolling.models import InfiniteScrolling
from test_project.apps.infinite_scrolling.tests.test_playwright.pages.detail_page import InfiniteScrollingDetailPage

if TYPE_CHECKING:
    from playwright.sync_api import Page
    from pytest_django.plugin import _LiveServer


@pytest.mark.django_db(transaction=True)
class TestDetailPage:
    def test_detail_page_loads(self, authenticated_page: Page, live_server: _LiveServer, transactional_db: None) -> None:
        item = InfiniteScrolling.objects.create(
            name='Test Item',
            description='Test Description'
        )

        detail_page = InfiniteScrollingDetailPage(authenticated_page, live_server.url, item.pk)
        detail_page.goto_page()

        assert detail_page.has_text('Test Item')
        assert detail_page.has_text('Test Description')

    def test_detail_page_shows_attributes(self, authenticated_page: Page, live_server: _LiveServer, transactional_db: None) -> None:
        item = InfiniteScrolling.objects.create(
            name='Detailed Item',
            description='Detailed Description'
        )

        detail_page = InfiniteScrollingDetailPage(authenticated_page, live_server.url, item.pk)
        detail_page.goto_page()

        assert detail_page.has_text('Name')
        assert detail_page.has_text('Created')
        assert detail_page.has_text('Description')
