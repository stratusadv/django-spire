from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator


class Dropdown:
    """Playwright component for django_spire/dropdown/dropdown.html"""

    menu_selector: str = '.position-absolute.shadow-lg.card'
    trigger_selector: str = '[x-bind="trigger"]'

    def __init__(self, parent_locator: Locator) -> None:
        self.parent = parent_locator

    @property
    def menu(self) -> Locator:
        return self.parent.page.locator(self.menu_selector).filter(
            has=self.parent.page.locator(':visible')
        ).first

    @property
    def trigger(self) -> Locator:
        return self.parent.locator(self.trigger_selector)

    def click_option(self, text: str) -> None:
        self.menu.locator(f'text={text}').click()

    def close(self) -> None:
        if self.is_open():
            self.trigger.click()

    def get_option(self, text: str) -> Locator:
        return self.menu.locator(f'text={text}')

    def has_option(self, text: str) -> bool:
        return self.get_option(text).is_visible()

    def is_open(self) -> bool:
        return self.menu.is_visible()

    def open(self) -> None:
        if not self.is_open():
            self.trigger.click()


class EllipsisDropdown(Dropdown):
    """Playwright component for django_spire/dropdown/ellipsis_dropdown.html"""

    trigger_selector: str = '.bi-three-dots-vertical'

    def click_delete(self) -> None:
        self.click_option('Delete')

    def click_edit(self) -> None:
        self.click_option('Edit')

    def click_view(self) -> None:
        self.click_option('View')

    def has_delete_option(self) -> bool:
        return self.has_option('Delete')

    def has_edit_option(self) -> bool:
        return self.has_option('Edit')

    def has_view_option(self) -> bool:
        return self.has_option('View')


class EllipsisModalDropdown(EllipsisDropdown):
    """
    Playwright component for django_spire/dropdown/ellipsis_modal_dropdown.html
    Dropdown options trigger modals via dispatch_modal_view()
    """

    pass


class EllipsisTableDropdown(EllipsisDropdown):
    """
    Playwright component for django_spire/dropdown/ellipsis_table_dropdown.html
    Used in table rows, positioned start-0 instead of end-0
    """
    trigger_selector: str = 'td .bi-three-dots-vertical'
