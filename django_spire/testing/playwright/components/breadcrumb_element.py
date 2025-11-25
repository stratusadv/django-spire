from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class Breadcrumb:
    """Playwright component for django_spire/element/breadcrumb_element.html"""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def breadcrumb(self) -> Locator:
        return self.page.locator('ol.breadcrumb')

    @property
    def items(self) -> Locator:
        return self.breadcrumb.locator('.breadcrumb-item')

    def click_item(self, index: int) -> None:
        link = self.get_item(index).locator('a')

        if link.count() > 0:
            link.click()

    def get_item(self, index: int) -> Locator:
        return self.items.nth(index)

    def get_item_count(self) -> int:
        return self.items.count()

    def get_item_href(self, index: int) -> str | None:
        link = self.get_item(index).locator('a')

        if link.count() > 0:
            return link.get_attribute('href')

        return None

    def get_item_text(self, index: int) -> str:
        return self.get_item(index).inner_text()

    def get_items_text(self) -> list[str]:
        return [self.get_item_text(i) for i in range(self.get_item_count())]

    def get_last_item_text(self) -> str:
        return self.items.last.inner_text()

    def is_item_clickable(self, index: int) -> bool:
        return self.get_item(index).locator('a').count() > 0

    def is_visible(self) -> bool:
        return self.breadcrumb.is_visible()
