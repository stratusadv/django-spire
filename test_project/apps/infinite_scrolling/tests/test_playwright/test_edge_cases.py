from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from test_project.apps.infinite_scrolling.models import InfiniteScrolling

if TYPE_CHECKING:
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.list_page import InfiniteScrollingListPage
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.table_page import InfiniteScrollingTablePage


@pytest.mark.django_db(transaction=True)
class TestEdgeCases:
    def test_rapid_scrolling(self, list_page: InfiniteScrollingListPage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        list_page.goto_page()

        for _ in range(3):
            list_page.scroll_to_bottom()
            list_page.page.wait_for_timeout(100)

        list_page.page.wait_for_timeout(1000)

        loaded_count = list_page.get_loaded_count()
        assert loaded_count > 10

    def test_sorting_refreshes_data(self, table_page: InfiniteScrollingTablePage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        table_page.goto_page()

        table_page.click_header('Name')
        table_page.page.wait_for_timeout(1000)

        final_count = table_page.get_loaded_count()
        assert final_count > 0

    def test_no_duplicate_items_loaded(self, list_page: InfiniteScrollingListPage, transactional_db: None) -> None:
        for i in range(25):
            InfiniteScrolling.objects.create(
                name=f'Unique Item {i}',
                description=f'Description {i}'
            )

        list_page.goto_page()

        list_page.scroll_to_bottom()
        list_page.page.wait_for_timeout(1000)

        items = list_page.page.locator('[data-row-id]')
        item_ids = [items.nth(i).get_attribute('data-row-id') for i in range(items.count())]

        assert len(item_ids) == len(set(item_ids))

    def test_batch_size_respected(self, list_page: InfiniteScrollingListPage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        list_page.goto_page()

        loaded_count = list_page.get_loaded_count()
        assert loaded_count == 10

    def test_total_count_accuracy(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        for i in range(15):
            InfiniteScrolling.objects.create(
                name=f'Item {i}',
                description=f'Desc {i}'
            )

        table_page.goto_page()

        total_count = table_page.get_total_count()
        assert total_count == 15
