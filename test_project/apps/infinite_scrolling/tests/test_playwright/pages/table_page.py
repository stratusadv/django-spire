from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import reverse

from django_spire.testing.playwright import BasePage, InfiniteScrollTable

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class InfiniteScrollingTablePage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self._table = InfiniteScrollTable(page)
        self.url = f'{base_url}{reverse("infinite_scrolling:page:table")}'

    @property
    def loaded_count_text(self) -> Locator:
        return self._table.loaded_count_text

    @property
    def rows(self) -> Locator:
        return self._table.rows

    @property
    def scroll_container(self) -> Locator:
        return self._table.scroll_container

    @property
    def select_all_checkbox(self) -> Locator:
        return self._table.select_all_checkbox

    @property
    def selected_count_text(self) -> Locator:
        return self._table.selected_count_text

    @property
    def skeleton_rows(self) -> Locator:
        return self._table.skeleton_rows

    @property
    def table(self) -> Locator:
        return self._table.table

    @property
    def total_count_text(self) -> Locator:
        return self._table.total_count_text

    def click_header(self, header_text: str) -> None:
        self._table.click_header(header_text)

    def deselect_all_rows(self) -> None:
        self._table.deselect_all_rows()

    def deselect_row(self, index: int) -> None:
        self._table.deselect_row(index)

    def get_first_row_text(self) -> str:
        return self._table.get_first_row_text()

    def get_header(self, header_text: str) -> Locator:
        return self._table.get_header(header_text)

    def get_loaded_count(self) -> int:
        return self._table.get_loaded_count()

    def get_selected_count(self) -> int:
        return self._table.get_selected_count()

    def get_sort_icon(self, header_text: str) -> Locator:
        return self._table.get_sort_icon(header_text)

    def get_total_count(self) -> int:
        return self._table.get_total_count()

    def goto_page(self) -> None:
        self.goto(self.url)
        self._table.wait_for_table()

    def is_sorted_ascending(self, header_text: str) -> bool:
        return self._table.is_sorted_ascending(header_text)

    def is_sorted_descending(self, header_text: str) -> bool:
        return self._table.is_sorted_descending(header_text)

    def scroll_to_bottom(self) -> None:
        self._table.scroll_to_bottom()

    def select_all_rows(self) -> None:
        self._table.select_all_rows()

    def select_row(self, index: int) -> None:
        self._table.select_row(index)

    def wait_for_count_to_increase(self, initial_count: int) -> None:
        self._table.wait_for_count_to_increase(initial_count)

    def wait_for_rows_to_load(self) -> None:
        self._table.wait_for_rows_to_load()
