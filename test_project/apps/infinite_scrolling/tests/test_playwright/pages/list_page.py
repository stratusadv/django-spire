from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import reverse

from test_project.apps.infinite_scrolling.tests.test_playwright.pages.base import BasePage

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class InfiniteScrollingListPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.url = f'{base_url}{reverse("infinite_scrolling:page:list")}'

    @property
    def loaded_count_text(self) -> Locator:
        return self.page.locator('[x-text="loaded_count"]')

    @property
    def total_count_text(self) -> Locator:
        return self.page.locator('[x-text="total_count"]')

    @property
    def scroll_container(self) -> Locator:
        return self.page.locator('.card [x-ref="scroll_container"]').last

    @property
    def items(self) -> Locator:
        return self.page.get_by_test_id('infinite-scrolling-item')

    @property
    def spinner(self) -> Locator:
        return self.page.locator('.spinner-border')

    @property
    def selected_count_text(self) -> Locator:
        return self.page.locator('[x-text="selected_rows.size"]')

    def goto_page(self) -> None:
        self.goto(self.url)
        self.wait_for_items_to_load()

    def wait_for_items_to_load(self) -> None:
        self.loaded_count_text.wait_for()

    def get_loaded_count(self) -> int:
        return int(self.loaded_count_text.inner_text())

    def get_total_count(self) -> int:
        return int(self.total_count_text.inner_text())

    def scroll_to_bottom(self) -> None:
        self.scroll_container.evaluate('el => el.scrollTop = el.scrollHeight')

    def wait_for_count_to_increase(self, initial_count: int) -> None:
        self.page.wait_for_function(
            f'() => parseInt(document.querySelector("[x-text=\\"loaded_count\\"]").textContent) > {initial_count}'
        )

    def get_item_count(self) -> int:
        return self.items.count()
