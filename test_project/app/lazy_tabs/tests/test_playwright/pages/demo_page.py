from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import reverse

from django_spire.testing.playwright import BasePage, LazyTab

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class LazyTabsDemoPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self._demo_tabs = LazyTab(page, '[data-testid="demo-tabs"]', 'demo_tab')
        self._user_tabs = LazyTab(page, '[data-testid="user-tabs"]', 'user_tab')
        self.url = f'{base_url}{reverse("lazy_tabs:page:demo")}'

    @property
    def demo_tab_sections(self) -> Locator:
        return self._demo_tabs.sections

    @property
    def demo_tab_triggers(self) -> Locator:
        return self._demo_tabs.triggers

    @property
    def user_tab_sections(self) -> Locator:
        return self._user_tabs.sections

    @property
    def user_tab_triggers(self) -> Locator:
        return self._user_tabs.triggers

    def click_demo_tab(self, index: int) -> None:
        self._demo_tabs.click_tab(index)

    def click_user_tab(self, index: int) -> None:
        self._user_tabs.click_tab(index)

    def get_demo_tab_section(self, index: int) -> Locator:
        return self._demo_tabs.get_section(index)

    def get_demo_tab_trigger(self, index: int) -> Locator:
        return self._demo_tabs.get_trigger(index)

    def get_demo_visible_section_text(self) -> str:
        return self._demo_tabs.get_visible_section_text()

    def get_url_param(self, param: str) -> str | None:
        if param == 'demo_tab':
            return self._demo_tabs.get_url_param()

        if param == 'user_tab':
            return self._user_tabs.get_url_param()

        return None

    def get_user_tab_section(self, index: int) -> Locator:
        return self._user_tabs.get_section(index)

    def get_user_tab_trigger(self, index: int) -> Locator:
        return self._user_tabs.get_trigger(index)

    def get_user_visible_section_text(self) -> str:
        return self._user_tabs.get_visible_section_text()

    def goto_page(self) -> None:
        self.goto(self.url)
        self.wait_for_tabs_to_load()

    def is_demo_tab_selected(self, index: int) -> bool:
        return self._demo_tabs.is_tab_selected(index)

    def is_user_tab_selected(self, index: int) -> bool:
        return self._user_tabs.is_tab_selected(index)

    def wait_for_tabs_to_load(self) -> None:
        self._demo_tabs.wait_for_tabs_to_load()
        self._user_tabs.wait_for_tabs_to_load()
