from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import reverse

from django_spire.testing.playwright import BasePage, InfiniteScrollList

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class InfiniteScrollingListPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self._infinite_scroll = InfiniteScrollList(page, '.card [x-ref="scroll_container"]')
        self.url = f'{base_url}{reverse("infinite_scrolling:page:list")}'

    @property
    def items(self) -> Locator:
        return self.page.get_by_test_id('infinite-scrolling-item')

    @property
    def loaded_count_text(self) -> Locator:
        return self._infinite_scroll.loaded_count_text

    @property
    def scroll_container(self) -> Locator:
        return self._infinite_scroll.scroll_container

    @property
    def selected_count_text(self) -> Locator:
        return self.page.locator('[x-text="selected_rows.size"]')

    @property
    def spinner(self) -> Locator:
        return self._infinite_scroll.spinner

    @property
    def total_count_text(self) -> Locator:
        return self._infinite_scroll.total_count_text

    def get_item_count(self) -> int:
        return self.items.count()

    def get_loaded_count(self) -> int:
        return self._infinite_scroll.get_loaded_count()

    def get_total_count(self) -> int:
        return self._infinite_scroll.get_total_count()

    def goto_page(self) -> None:
        self.goto(self.url)
        self._infinite_scroll.wait_for_items_to_load()

    def scroll_to_bottom(self) -> None:
        self._infinite_scroll.scroll_to_bottom()

    def wait_for_count_to_increase(self, initial_count: int) -> None:
        self._infinite_scroll.wait_for_count_to_increase(initial_count)

    def wait_for_items_to_load(self) -> None:
        self._infinite_scroll.wait_for_items_to_load()
