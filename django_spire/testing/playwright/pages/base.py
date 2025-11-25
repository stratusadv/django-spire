from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.base_url = base_url
        self.page = page

    def goto(self, url: str) -> None:
        self.page.goto(url)

    def has_text(self, text: str) -> bool:
        return text in self.page.locator('body').inner_text()

    def wait_for_load_state(self, state: str = 'networkidle') -> None:
        self.page.wait_for_load_state(state)

    def wait_for_timeout(self, timeout: int) -> None:
        self.page.wait_for_timeout(timeout)
