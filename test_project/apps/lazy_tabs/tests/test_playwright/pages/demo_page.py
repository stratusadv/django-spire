from __future__ import annotations

import re

from typing import TYPE_CHECKING

from django.urls import reverse

from test_project.apps.lazy_tabs.tests.test_playwright.pages.base import BasePage

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class LazyTabsDemoPage(BasePage):
    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.url = f'{base_url}{reverse("lazy_tabs:page:demo")}'

    @property
    def demo_tab_triggers(self) -> Locator:
        return self.page.locator('[data-testid="demo-tabs"] [role="tab"]')

    @property
    def demo_tab_sections(self) -> Locator:
        return self.page.locator('[data-testid="demo-tabs"] [role="tabpanel"]')

    @property
    def user_tab_triggers(self) -> Locator:
        return self.page.locator('[data-testid="user-tabs"] [role="tab"]')

    @property
    def user_tab_sections(self) -> Locator:
        return self.page.locator('[data-testid="user-tabs"] [role="tabpanel"]')

    def goto_page(self) -> None:
        self.goto(self.url)
        self.wait_for_tabs_to_load()

    def wait_for_tabs_to_load(self) -> None:
        self.demo_tab_triggers.first.wait_for()
        self.user_tab_triggers.first.wait_for()

    def get_demo_tab_trigger(self, index: int) -> Locator:
        return self.demo_tab_triggers.nth(index)

    def get_demo_tab_section(self, index: int) -> Locator:
        return self.demo_tab_sections.nth(index)

    def get_user_tab_trigger(self, index: int) -> Locator:
        return self.user_tab_triggers.nth(index)

    def get_user_tab_section(self, index: int) -> Locator:
        return self.user_tab_sections.nth(index)

    def click_demo_tab(self, index: int) -> None:
        self.get_demo_tab_trigger(index).click()

    def click_user_tab(self, index: int) -> None:
        self.get_user_tab_trigger(index).click()

    def is_demo_tab_selected(self, index: int) -> bool:
        trigger = self.get_demo_tab_trigger(index)
        classes = trigger.get_attribute('class') or ''
        return 'tab-item' in classes

    def is_user_tab_selected(self, index: int) -> bool:
        trigger = self.get_user_tab_trigger(index)
        classes = trigger.get_attribute('class') or ''
        return 'tab-item' in classes

    def get_demo_visible_section_text(self) -> str:
        for i in range(self.demo_tab_sections.count()):
            section = self.demo_tab_sections.nth(i)
            if section.is_visible():
                return section.inner_text()
        return ''

    def get_user_visible_section_text(self) -> str:
        for i in range(self.user_tab_sections.count()):
            section = self.user_tab_sections.nth(i)
            if section.is_visible():
                return section.inner_text()
        return ''

    def get_url_param(self, param: str) -> str | None:
        url = self.page.url
        match = re.search(f'{param}=([^&]+)', url)

        if match:
            return match.group(1)

        return None
