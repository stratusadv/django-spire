from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class Card:
    """Playwright component for django_spire/card/card.html"""

    def __init__(self, page: Page, card_selector: str = '.card') -> None:
        self.card_selector = card_selector
        self.page = page

    @property
    def card(self) -> Locator:
        return self.page.locator(self.card_selector).first

    @property
    def content(self) -> Locator:
        return self.card.locator('.card-body, .p-3').first

    def is_visible(self) -> bool:
        return self.card.is_visible()


class TitleCard(Card):
    """Playwright component for django_spire/card/title_card.html"""

    @property
    def button(self) -> Locator:
        return self.card.locator('.col-auto.d-flex').first

    @property
    def dropdown_content(self) -> Locator:
        return self.card.locator('[x-show="card_title_dropdown"]')

    @property
    def title(self) -> Locator:
        return self.card.locator('.card-title').first

    def click_button(self) -> None:
        self.button.locator('button, a').first.click()

    def get_title_text(self) -> str:
        return self.title.inner_text()

    def has_button(self) -> bool:
        return self.button.locator('button, a').count() > 0

    def is_dropdown_open(self) -> bool:
        return self.dropdown_content.is_visible()

    def toggle_dropdown(self) -> None:
        self.card.locator('[\\@click*="toggle_card_title_dropdown"]').click()


class FormCard(TitleCard):
    """Playwright component for django_spire/card/form_card.html"""

    @property
    def description(self) -> Locator:
        return self.card.locator('.mb-3').first

    @property
    def form(self) -> Locator:
        return self.card.locator('form')

    def fill_field(self, name: str, value: str) -> None:
        self.form.locator(f'[name="{name}"]').fill(value)

    def get_field_value(self, name: str) -> str:
        return self.form.locator(f'[name="{name}"]').input_value()

    def submit(self) -> None:
        self.form.locator('button[type="submit"], input[type="submit"]').click()


class InfiniteScrollCard(TitleCard):
    """Playwright component for django_spire/card/infinite_scroll_card.html"""

    @property
    def loaded_count_text(self) -> Locator:
        return self.card.locator('[x-text="loaded_count"]')

    @property
    def scroll_container(self) -> Locator:
        return self.card.locator('[x-ref="scroll_container"]')

    @property
    def total_count_text(self) -> Locator:
        return self.card.locator('[x-text="total_count"]')

    def get_loaded_count(self) -> int:
        return int(self.loaded_count_text.inner_text())

    def get_total_count(self) -> int:
        return int(self.total_count_text.inner_text())

    def scroll_to_bottom(self) -> None:
        self.scroll_container.evaluate('el => el.scrollTop = el.scrollHeight')
