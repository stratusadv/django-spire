from __future__ import annotations

import re

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class LazyTab:
    """Playwright component for django_spire/lazy_tab/lazy_tab.html"""

    selected_class: str = 'tab-item'

    def __init__(self, page: Page, container_selector: str, tab_id: str | None = None) -> None:
        self.container_selector = container_selector
        self.page = page
        self.tab_id = tab_id

    @property
    def container(self) -> Locator:
        return self.page.locator(self.container_selector)

    @property
    def sections(self) -> Locator:
        return self.container.locator('[role="tabpanel"]')

    @property
    def triggers(self) -> Locator:
        return self.container.locator('[role="tab"]')

    def click_tab(self, index: int) -> None:
        self.get_trigger(index).click()

    def get_section(self, index: int) -> Locator:
        return self.sections.nth(index)

    def get_section_count(self) -> int:
        return self.sections.count()

    def get_trigger(self, index: int) -> Locator:
        return self.triggers.nth(index)

    def get_trigger_count(self) -> int:
        return self.triggers.count()

    def get_url_param(self) -> str | None:
        if not self.tab_id:
            return None

        url = self.page.url
        match = re.search(f'{self.tab_id}=([^&]+)', url)

        if match:
            return match.group(1)

        return None

    def get_visible_section(self) -> Locator | None:
        for i in range(self.sections.count()):
            section = self.sections.nth(i)

            if section.is_visible():
                return section

        return None

    def get_visible_section_text(self) -> str:
        section = self.get_visible_section()

        if section:
            return section.inner_text()

        return ''

    def is_loading(self, index: int) -> bool:
        section = self.get_section(index)
        spinner = section.locator('.spinner-border')
        return spinner.is_visible()

    def is_tab_selected(self, index: int) -> bool:
        trigger = self.get_trigger(index)
        classes = trigger.get_attribute('class') or ''
        return self.selected_class in classes

    def wait_for_section_content(self, index: int, timeout: int = 5000) -> None:
        section = self.get_section(index)
        section.locator('.spinner-border').wait_for(state='hidden', timeout=timeout)

    def wait_for_tabs_to_load(self) -> None:
        self.triggers.first.wait_for()
