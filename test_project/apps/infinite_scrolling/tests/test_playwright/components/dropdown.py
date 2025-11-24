from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator


class EllipsisDropdown:
    def __init__(self, parent_locator: Locator) -> None:
        self.parent = parent_locator
        self.trigger = parent_locator.locator('.bi-three-dots-vertical')

    @property
    def menu(self) -> Locator:
        return self.parent.page.locator('.position-absolute.shadow-lg.card').filter(has=self.parent.page.locator('visible=true')).first

    def open(self) -> None:
        self.trigger.click()

    def is_open(self) -> bool:
        return self.menu.is_visible()

    def has_view_option(self) -> bool:
        return self.menu.locator('text=View').is_visible()

    def has_edit_option(self) -> bool:
        return self.menu.locator('text=Edit').is_visible()

    def has_delete_option(self) -> bool:
        return self.menu.locator('text=Delete').is_visible()

    def click_view(self) -> None:
        self.menu.locator('text=View').click()

    def click_edit(self) -> None:
        self.menu.locator('text=Edit').click()

    def click_delete(self) -> None:
        self.menu.locator('text=Delete').click()
