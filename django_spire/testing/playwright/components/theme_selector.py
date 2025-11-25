from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class ThemeSelector:
    """Playwright component for django_spire/theme/element/theme_selector.html"""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def icon(self) -> Locator:
        return self.page.locator('.bi-sun-fill, .bi-moon-fill').first

    def click(self) -> None:
        self.icon.click()

    def get_current_mode(self) -> str:
        html = self.page.locator('html')
        return html.get_attribute('data-theme') or 'light'

    def get_current_theme_family(self) -> str:
        html = self.page.locator('html')
        return html.get_attribute('data-theme-family') or ''

    def is_dark_mode(self) -> bool:
        return self.get_current_mode() == 'dark'

    def is_light_mode(self) -> bool:
        return self.get_current_mode() == 'light'

    def is_visible(self) -> bool:
        return self.icon.is_visible()

    def toggle(self) -> None:
        self.click()

    def wait_for_theme_change(self, expected_mode: str, timeout: int = 5000) -> None:
        self.page.wait_for_function(
            f'() => document.documentElement.getAttribute("data-theme") === "{expected_mode}"',
            timeout=timeout
        )
