from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class SideNavigation:
    """Playwright component for django_spire/navigation/side_navigation.html"""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def container(self) -> Locator:
        return self.page.locator('.side-navigation')

    @property
    def links(self) -> Locator:
        return self.container.locator('a.nav-link')

    @property
    def scroll_container(self) -> Locator:
        return self.container.locator('[x-ref="scroll_container"]')

    def click_link(self, text: str) -> None:
        self.get_link_by_text(text).click()

    def get_link_by_text(self, text: str) -> Locator:
        return self.container.locator(f'a.nav-link:has-text("{text}")')

    def get_link_count(self) -> int:
        return self.links.count()

    def get_link_texts(self) -> list[str]:
        return [self.links.nth(i).inner_text() for i in range(self.get_link_count())]

    def has_link(self, text: str) -> bool:
        return self.get_link_by_text(text).count() > 0

    def is_visible(self) -> bool:
        return self.container.is_visible()


class TopNavigation:
    """Playwright component for django_spire/navigation/top_navigation.html"""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def container(self) -> Locator:
        return self.page.locator('.top-navigation')

    @property
    def notification_bell(self) -> Locator:
        return self.container.locator('.bi-bell')

    @property
    def theme_selector(self) -> Locator:
        return self.container.locator('.bi-sun-fill, .bi-moon-fill')

    @property
    def title(self) -> Locator:
        return self.container.locator('.fs-5.fw-bold, .fs-md-1.fw-bold').first

    @property
    def user_menu(self) -> Locator:
        return self.container.locator('.bi-person-circle')

    def click_notification_bell(self) -> None:
        self.notification_bell.click()

    def click_theme_selector(self) -> None:
        self.theme_selector.click()

    def click_user_menu(self) -> None:
        self.user_menu.click()

    def get_title_text(self) -> str:
        return self.title.inner_text()

    def is_visible(self) -> bool:
        return self.container.is_visible()


class UserMenu:
    """Playwright component for user dropdown menu in top navigation"""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def menu(self) -> Locator:
        return self.page.locator('.dropdown-menu[aria-labelledby="dropdownMenuButton1"]')

    @property
    def trigger(self) -> Locator:
        return self.page.locator('#dropdownMenuButton1')

    def click_admin_panel(self) -> None:
        self.menu.locator('a:has-text("Admin Panel")').click()

    def click_change_password(self) -> None:
        self.menu.locator('a:has-text("Change Password")').click()

    def click_logout(self) -> None:
        self.menu.locator('a:has-text("Logout")').click()

    def click_theme_dashboard(self) -> None:
        self.menu.locator('a:has-text("Theme Dashboard")').click()

    def is_open(self) -> bool:
        return self.menu.is_visible()

    def open(self) -> None:
        if not self.is_open():
            self.trigger.click()
