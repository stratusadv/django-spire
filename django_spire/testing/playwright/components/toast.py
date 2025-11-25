from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class Toast:
    """Playwright component for django_spire/messages/messages.html"""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def container(self) -> Locator:
        return self.page.locator('.fixed-top[\\@notify\\.window]')

    @property
    def toasts(self) -> Locator:
        return self.container.locator('[x-data*="show:"]')

    def get_toast(self, index: int = 0) -> Locator:
        return self.toasts.nth(index)

    def get_toast_count(self) -> int:
        return self.toasts.count()

    def get_toast_icon(self, index: int = 0) -> Locator:
        return self.get_toast(index).locator('i.bi').first

    def get_toast_message(self, index: int = 0) -> str:
        return self.get_toast(index).locator('[x-text="notification.message"]').inner_text()

    def get_toast_type(self, index: int = 0) -> str:
        toast = self.get_toast(index)
        classes = toast.get_attribute('class') or ''

        if 'border-app-success' in classes:
            return 'success'

        if 'border-app-warning' in classes:
            return 'warning'

        if 'border-app-danger' in classes:
            return 'error'

        if 'border-app-primary' in classes:
            return 'info'

        return 'unknown'

    def close_toast(self, index: int = 0) -> None:
        self.get_toast(index).locator('.bi-x-lg').click()

    def has_success_toast(self) -> bool:
        return self.page.locator('.border-app-success').count() > 0

    def has_warning_toast(self) -> bool:
        return self.page.locator('.border-app-warning').count() > 0

    def has_error_toast(self) -> bool:
        return self.page.locator('.border-app-danger').count() > 0

    def has_info_toast(self) -> bool:
        return self.page.locator('.border-app-primary').count() > 0

    def wait_for_toast(self, timeout: int = 5000) -> None:
        self.toasts.first.wait_for(state='visible', timeout=timeout)

    def wait_for_toast_to_disappear(self, timeout: int = 10000) -> None:
        self.toasts.first.wait_for(state='hidden', timeout=timeout)
