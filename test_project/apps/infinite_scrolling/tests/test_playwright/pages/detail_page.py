from __future__ import annotations

from typing import TYPE_CHECKING

from django.urls import reverse

from test_project.apps.infinite_scrolling.tests.test_playwright.pages.base import BasePage

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class InfiniteScrollingDetailPage(BasePage):
    def __init__(self, page: Page, base_url: str, pk: int) -> None:
        super().__init__(page, base_url)
        self.pk = pk
        self.url = f'{base_url}{reverse("infinite_scrolling:page:detail", kwargs={"pk": pk})}'

    @property
    def detail_content(self) -> Locator:
        return self.page.get_by_test_id('detail-card-content')

    def goto_page(self) -> None:
        self.goto(self.url)
        self.detail_content.wait_for()

    def has_text(self, text: str) -> bool:
        return self.page.locator('body').inner_text().__contains__(text)

    def get_attribute_value(self, attribute_title: str) -> str:
        attribute_section = self.page.locator(f'.fs-7:has-text("{attribute_title}")').locator('..')
        return attribute_section.locator('.fs-6').inner_text()
