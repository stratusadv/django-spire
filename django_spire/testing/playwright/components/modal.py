from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class Modal:
    """Playwright component for django_spire/modal/modal.html"""

    def __init__(self, page: Page) -> None:
        self.page = page

    @property
    def close_button(self) -> Locator:
        return self.modal.locator('[\\@click*="close_modal"]').first

    @property
    def content(self) -> Locator:
        return self.modal.locator('.bg-app-layer-one.card')

    @property
    def modal(self) -> Locator:
        return self.page.locator('[x-show="show_modal"]').last

    @property
    def overlay(self) -> Locator:
        return self.page.locator('[\\@click="close_modal"]').first

    def close(self) -> None:
        self.close_button.click()

    def close_by_overlay(self) -> None:
        self.overlay.click()

    def is_open(self) -> bool:
        return self.modal.is_visible()

    def wait_for_close(self, timeout: int = 5000) -> None:
        self.modal.wait_for(state='hidden', timeout=timeout)

    def wait_for_open(self, timeout: int = 5000) -> None:
        self.modal.wait_for(state='visible', timeout=timeout)


class TitleModal(Modal):
    """Playwright component for django_spire/modal/title_modal.html"""

    @property
    def title(self) -> Locator:
        return self.modal.locator('.text-uppercase.text-app-secondary-dark.h6').first

    def get_title_text(self) -> str:
        return self.title.inner_text()


class FormModal(TitleModal):
    """Playwright component for modals containing forms"""

    @property
    def cancel_button(self) -> Locator:
        return self.modal.locator('button:has-text("Cancel"), [type="button"]:has-text("Cancel")').first

    @property
    def form(self) -> Locator:
        return self.modal.locator('form')

    @property
    def submit_button(self) -> Locator:
        return self.modal.locator('button[type="submit"], input[type="submit"]').first

    def cancel(self) -> None:
        self.cancel_button.click()

    def fill_field(self, name: str, value: str) -> None:
        self.form.locator(f'[name="{name}"]').fill(value)

    def get_field_value(self, name: str) -> str:
        return self.form.locator(f'[name="{name}"]').input_value()

    def submit(self) -> None:
        self.submit_button.click()


class DeleteModal(TitleModal):
    """Playwright component for delete confirmation modals"""

    @property
    def cancel_button(self) -> Locator:
        return self.modal.locator('button:has-text("Cancel")').first

    @property
    def confirm_button(self) -> Locator:
        return self.modal.locator('button:has-text("Delete"), button:has-text("Confirm")').first

    def cancel(self) -> None:
        self.cancel_button.click()

    def confirm(self) -> None:
        self.confirm_button.click()
