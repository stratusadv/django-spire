from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from test_project.apps.infinite_scrolling.models import InfiniteScrolling

if TYPE_CHECKING:
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.list_page import InfiniteScrollingListPage
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.table_page import InfiniteScrollingTablePage


@pytest.mark.django_db(transaction=True)
class TestResponsiveness:
    def test_table_responsive_columns(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(name='Test', description='Test Desc')

        table_page.goto_page()

        table_page.page.set_viewport_size({'width': 768, 'height': 1024})
        table_page.page.wait_for_timeout(200)

        created_header = table_page.get_header('Created')
        assert created_header.count() > 0

    def test_mobile_list_view(self, list_page: InfiniteScrollingListPage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        list_page.page.set_viewport_size({'width': 375, 'height': 667})
        list_page.goto_page()

        assert list_page.loaded_count_text.is_visible()
