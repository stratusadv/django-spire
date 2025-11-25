from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class NotificationBell:
    """Playwright component for django_spire/notification/app/element/notification_bell.html"""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def badge(self) -> Locator:
        return self.bell.locator('.badge, .position-absolute')

    @property
    def bell(self) -> Locator:
        return self.page.locator('.bi-bell').first

    @property
    def dropdown(self) -> Locator:
        return self.page.locator('.notification-dropdown, [x-show*="notification"]')

    def click(self) -> None:
        self.bell.click()

    def get_badge_count(self) -> int:
        if not self.has_badge():
            return 0

        text = self.badge.inner_text()

        if text.isdigit():
            return int(text)

        return 0

    def has_badge(self) -> bool:
        return self.badge.count() > 0 and self.badge.is_visible()

    def has_notifications(self) -> bool:
        return self.has_badge() and self.get_badge_count() > 0

    def is_dropdown_open(self) -> bool:
        return self.dropdown.is_visible()

    def is_visible(self) -> bool:
        return self.bell.is_visible()

    def open_dropdown(self) -> None:
        if not self.is_dropdown_open():
            self.click()

    def close_dropdown(self) -> None:
        if self.is_dropdown_open():
            self.click()
