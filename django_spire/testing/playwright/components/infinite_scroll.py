from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class InfiniteScroll:
    """
    Playwright component for django_spire/infinite_scroll/base.html
    and django_spire/infinite_scroll/scroll.html
    """

    def __init__(self, page: Page, container_selector: str = '[x-ref="scroll_container"]') -> None:
        self.container_selector = container_selector
        self.page = page

    @property
    def content_container(self) -> Locator:
        return self.page.locator('[x-ref="content_container"]')

    @property
    def loaded_count_text(self) -> Locator:
        return self.page.locator('[x-text="loaded_count"]')

    @property
    def scroll_container(self) -> Locator:
        return self.page.locator(self.container_selector)

    @property
    def spinner(self) -> Locator:
        return self.page.locator('.spinner-border')

    @property
    def total_count_text(self) -> Locator:
        return self.page.locator('[x-text="total_count"]')

    def get_loaded_count(self) -> int:
        return int(self.loaded_count_text.inner_text())

    def get_total_count(self) -> int:
        return int(self.total_count_text.inner_text())

    def is_loading(self) -> bool:
        return self.spinner.is_visible()

    def scroll_to_bottom(self) -> None:
        self.scroll_container.evaluate('el => el.scrollTop = el.scrollHeight')

    def scroll_to_top(self) -> None:
        self.scroll_container.evaluate('el => el.scrollTop = 0')

    def wait_for_count_to_increase(self, initial_count: int, timeout: int = 5000) -> None:
        self.page.wait_for_function(
            f'() => parseInt(document.querySelector("[x-text=\\"loaded_count\\"]").textContent) > {initial_count}',
            timeout=timeout
        )

    def wait_for_items_to_load(self) -> None:
        self.loaded_count_text.wait_for()


class InfiniteScrollList(InfiniteScroll):
    """Playwright component for infinite scroll with list items"""

    item_selector: str = '[data-row-id]'

    @property
    def items(self) -> Locator:
        return self.page.locator(self.item_selector)

    def get_item(self, index: int) -> Locator:
        return self.items.nth(index)

    def get_item_count(self) -> int:
        return self.items.count()

    def get_item_ids(self) -> list[str]:
        items = self.items
        return [items.nth(i).get_attribute('data-row-id') for i in range(items.count())]


class InfiniteScrollTable(InfiniteScroll):
    """Playwright component for django_spire/table/base.html"""

    row_selector: str = 'tbody tr[data-row-id]'
    skeleton_selector: str = '.skeleton-box'

    def __init__(self, page: Page, container_selector: str = '.table-container[x-ref="scroll_container"]') -> None:
        super().__init__(page, container_selector)

    @property
    def rows(self) -> Locator:
        return self.page.locator(self.row_selector)

    @property
    def select_all_checkbox(self) -> Locator:
        return self.page.locator('thead input[type="checkbox"]')

    @property
    def selected_count_text(self) -> Locator:
        return self.page.locator('[x-text="selected_rows.size"]')

    @property
    def skeleton_rows(self) -> Locator:
        return self.page.locator(self.skeleton_selector)

    @property
    def table(self) -> Locator:
        return self.page.locator('table')

    def click_header(self, header_text: str) -> None:
        self.get_header(header_text).click()

    def deselect_all_rows(self) -> None:
        self.select_all_checkbox.click()

    def deselect_row(self, index: int) -> None:
        self.get_row(index).locator('input[type="checkbox"]').click()

    def get_first_row_text(self) -> str:
        return self.rows.first.inner_text()

    def get_header(self, header_text: str) -> Locator:
        return self.page.locator(f'th:has-text("{header_text}")')

    def get_row(self, index: int) -> Locator:
        return self.rows.nth(index)

    def get_row_count(self) -> int:
        return self.rows.count()

    def get_selected_count(self) -> int:
        return int(self.selected_count_text.inner_text())

    def get_sort_icon(self, header_text: str) -> Locator:
        return self.get_header(header_text).locator('i.bi')

    def is_sorted_ascending(self, header_text: str) -> bool:
        icon = self.get_sort_icon(header_text)
        return 'bi-chevron-up' in (icon.get_attribute('class') or '')

    def is_sorted_descending(self, header_text: str) -> bool:
        icon = self.get_sort_icon(header_text)
        return 'bi-chevron-down' in (icon.get_attribute('class') or '')

    def select_all_rows(self) -> None:
        self.select_all_checkbox.click()

    def select_row(self, index: int) -> None:
        self.get_row(index).locator('input[type="checkbox"]').click()

    def wait_for_rows_to_load(self) -> None:
        self.rows.first.wait_for()

    def wait_for_table(self) -> None:
        self.table.wait_for()
