from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class FilterForm:
    """Playwright component for django_spire/filtering/form/base_session_filter_form.html"""

    def __init__(self, page: Page, form_selector: str = 'form[action*="filter"], form[action*="search"]') -> None:
        self.form_selector = form_selector
        self.page = page

    @property
    def clear_button(self) -> Locator:
        return self.form.locator('input[value="Clear"], button:has-text("Clear")')

    @property
    def filter_button(self) -> Locator:
        return self.form.locator('input[value="Filter"], button:has-text("Filter")')

    @property
    def form(self) -> Locator:
        return self.page.locator(self.form_selector).first

    @property
    def search_button(self) -> Locator:
        return self.form.locator('input[value="Search"], button:has-text("Search")')

    @property
    def search_input(self) -> Locator:
        return self.form.locator('input[name="search"], input[placeholder*="Search"]')

    def clear(self) -> None:
        self.clear_button.click()

    def fill_field(self, name: str, value: str) -> None:
        self.form.locator(f'[name="{name}"]').fill(value)

    def filter(self) -> None:
        self.filter_button.click()

    def get_field_value(self, name: str) -> str:
        return self.form.locator(f'[name="{name}"]').input_value()

    def search(self, query: str) -> None:
        self.search_input.fill(query)
        self.search_button.click()

    def select_option(self, name: str, value: str) -> None:
        self.form.locator(f'select[name="{name}"]').select_option(value)

    def submit(self) -> None:
        submit_btn = self.form.locator('button[type="submit"], input[type="submit"]').first
        submit_btn.click()
