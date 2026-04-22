from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import reverse

from django_spire.testing.playwright import BasePage

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class InfiniteScrollingCardPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.url = f'{base_url}{reverse("infinite_scrolling:page:cards")}'

    @property
    def loaded_count_texts(self) -> Locator:
        return self.page.locator('[x-text="loaded_count"]')

    @property
    def scroll_containers(self) -> Locator:
        return self.page.locator('[data-scroll-id]')

    def get_container_count(self) -> int:
        return self.scroll_containers.count()

    def get_loaded_counts(self) -> list[int]:
        return [
            int(self.loaded_count_texts.nth(i).inner_text())
            for i in range(self.loaded_count_texts.count())
        ]

    def goto_page(self) -> None:
        self.goto(self.url)
        self.wait_for_containers_to_load()

    def scroll_container_to_bottom(self, index: int) -> None:
        container = self.scroll_containers.nth(index)
        container.locator('[x-ref="scroll_container"]').evaluate('el => el.scrollTop = el.scrollHeight')

    def wait_for_containers_to_load(self) -> None:
        self.scroll_containers.first.wait_for()
