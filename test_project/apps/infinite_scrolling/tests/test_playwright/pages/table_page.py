from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import reverse

from test_project.apps.infinite_scrolling.tests.test_playwright.pages.base import BasePage

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class InfiniteScrollingTablePage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.url = f'{base_url}{reverse("infinite_scrolling:page:table")}'

    @property
    def table(self) -> Locator:
        return self.page.locator('table')

    @property
    def loaded_count_text(self) -> Locator:
        return self.page.locator('[x-text="loaded_count"]')

    @property
    def total_count_text(self) -> Locator:
        return self.page.locator('[x-text="total_count"]')

    @property
    def selected_count_text(self) -> Locator:
        return self.page.locator('[x-text="selected_rows.size"]')

    @property
    def scroll_container(self) -> Locator:
        return self.page.locator('.table-container[x-ref="scroll_container"]')

    @property
    def rows(self) -> Locator:
        return self.page.locator('tbody tr[data-row-id]')

    @property
    def skeleton_rows(self) -> Locator:
        return self.page.locator('.skeleton-box')

    @property
    def select_all_checkbox(self) -> Locator:
        return self.page.locator('thead input[type="checkbox"]')

    def goto_page(self) -> None:
        self.goto(self.url)
        self.table.wait_for()

    def wait_for_rows_to_load(self) -> None:
        self.rows.first.wait_for()

    def get_loaded_count(self) -> int:
        return int(self.loaded_count_text.inner_text())

    def get_total_count(self) -> int:
        return int(self.total_count_text.inner_text())

    def get_selected_count(self) -> int:
        return int(self.selected_count_text.inner_text())

    def scroll_to_bottom(self) -> None:
        self.scroll_container.evaluate('el => el.scrollTop = el.scrollHeight')

    def wait_for_count_to_increase(self, initial_count: int) -> None:
        self.page.wait_for_function(
            f'() => parseInt(document.querySelector("[x-text=\\"loaded_count\\"]").textContent) > {initial_count}'
        )

    def get_header(self, header_text: str) -> Locator:
        return self.page.locator(f'th:has-text("{header_text}")')

    def click_header(self, header_text: str) -> None:
        self.get_header(header_text).click()

    def get_sort_icon(self, header_text: str) -> Locator:
        return self.get_header(header_text).locator('i.bi')

    def is_sorted_ascending(self, header_text: str) -> bool:
        icon = self.get_sort_icon(header_text)
        return 'bi-chevron-up' in icon.get_attribute('class')

    def is_sorted_descending(self, header_text: str) -> bool:
        icon = self.get_sort_icon(header_text)
        return 'bi-chevron-down' in icon.get_attribute('class')

    def get_first_row_text(self) -> str:
        return self.rows.first.inner_text()

    def select_all_rows(self) -> None:
        self.select_all_checkbox.click()

    def deselect_all_rows(self) -> None:
        self.select_all_checkbox.click()

    def select_row(self, index: int) -> None:
        self.rows.nth(index).locator('input[type="checkbox"]').click()

    def deselect_row(self, index: int) -> None:
        self.rows.nth(index).locator('input[type="checkbox"]').click()
