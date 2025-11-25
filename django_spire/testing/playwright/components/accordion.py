from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator


class Accordion:
    """Playwright component for django_spire/accordion/accordion.html"""

    def __init__(self, parent_locator: Locator) -> None:
        self.parent = parent_locator

    @property
    def content(self) -> Locator:
        return self.parent.locator('[x-show="show_accordion"]')

    @property
    def toggle(self) -> Locator:
        return self.parent.locator('[\\@click*="toggle"]').first

    def close(self) -> None:
        if self.is_open():
            self.toggle.click()

    def is_open(self) -> bool:
        return self.content.is_visible()

    def open(self) -> None:
        if not self.is_open():
            self.toggle.click()


class NavAccordion(Accordion):
    """Playwright component for django_spire/navigation/accordion/nav_accordion.html"""

    @property
    def chevron(self) -> Locator:
        return self.parent.locator('.bi-chevron-right, .bi-chevron-down')

    @property
    def icon(self) -> Locator:
        return self.parent.locator('i.fs-6').first

    @property
    def title(self) -> Locator:
        return self.parent.locator('span.h6')

    def get_title_text(self) -> str:
        return self.title.inner_text()

    def is_expanded(self) -> bool:
        chevron_classes = self.chevron.get_attribute('class') or ''
        return 'bi-chevron-down' in chevron_classes
