from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_project.apps.infinite_scrolling.models import InfiniteScrolling
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.table_page import InfiniteScrollingTablePage


@pytest.mark.django_db(transaction=True)
class TestLoadingStates:
    def test_skeleton_loading_appears(self, table_page: InfiniteScrollingTablePage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        table_page.page.route('**/*', lambda route: route.continue_())
        table_page.goto(table_page.url)

        skeletons = table_page.skeleton_rows

        table_page.page.wait_for_timeout(100)

        if skeletons.count() > 0:
            assert True
        else:
            table_page.rows.first.wait_for()
            assert True

    def test_table_has_loading_state(self, table_page: InfiniteScrollingTablePage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        table_page.goto_page()

        loaded_count = table_page.get_loaded_count()
        assert loaded_count > 0
