from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_project.apps.infinite_scrolling.models import InfiniteScrolling
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.card_page import InfiniteScrollingCardPage


@pytest.mark.django_db(transaction=True)
class TestCardPage:
    def test_card_page_loads(self, card_page: InfiniteScrollingCardPage) -> None:
        card_page.goto_page()

        assert card_page.page.locator('h1').inner_text().__contains__('Infinite Scrolling - Cards')

    def test_multiple_scroll_containers(self, card_page: InfiniteScrollingCardPage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        card_page.goto_page()

        assert card_page.get_container_count() >= 2

    def test_card_scroll_independence(self, card_page: InfiniteScrollingCardPage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        card_page.goto_page()

        card_page.scroll_container_to_bottom(0)
        card_page.page.wait_for_timeout(800)

        counts = card_page.get_loaded_counts()
        assert len(set(counts)) > 1
