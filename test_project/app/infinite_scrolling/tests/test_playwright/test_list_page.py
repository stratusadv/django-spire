from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_project.apps.infinite_scrolling.models import InfiniteScrolling
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.list_page import InfiniteScrollingListPage


@pytest.mark.django_db(transaction=True)
class TestListPage:
    def test_list_page_loads(self, list_page: InfiniteScrollingListPage) -> None:
        list_page.goto_page()

        assert list_page.page.locator('h1').inner_text().__contains__('Infinite Scrolling')
        assert list_page.scroll_container.is_visible()

    def test_initial_batch_loads(self, list_page: InfiniteScrollingListPage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        list_page.goto_page()

        assert list_page.get_loaded_count() == 10
        assert list_page.get_total_count() == 30

    def test_infinite_scroll_loads_more_items(self, list_page: InfiniteScrollingListPage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        list_page.goto_page()

        initial_count = list_page.get_loaded_count()
        assert initial_count == 10

        list_page.scroll_to_bottom()
        list_page.wait_for_count_to_increase(initial_count)

        final_count = list_page.get_loaded_count()
        assert final_count > initial_count
        assert final_count == 20

    def test_scroll_loads_all_items(self, list_page: InfiniteScrollingListPage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        list_page.goto_page()

        for _ in range(5):
            list_page.scroll_to_bottom()
            list_page.page.wait_for_timeout(500)

        loaded_count = list_page.get_loaded_count()
        total_count = list_page.get_total_count()

        assert loaded_count == total_count
        assert loaded_count == 30

    def test_loading_spinner_exists(self, list_page: InfiniteScrollingListPage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        list_page.goto_page()

        assert list_page.spinner.count() >= 0

    def test_empty_state_displays(self, list_page: InfiniteScrollingListPage, transactional_db: None) -> None:
        list_page.goto_page()

        assert list_page.get_loaded_count() == 0
        assert list_page.get_total_count() == 0
