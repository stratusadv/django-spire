from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from test_project.apps.infinite_scrolling.models import InfiniteScrolling
from test_project.apps.infinite_scrolling.tests.test_playwright.components.dropdown import EllipsisDropdown

if TYPE_CHECKING:
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.list_page import InfiniteScrollingListPage
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.table_page import InfiniteScrollingTablePage


@pytest.mark.django_db(transaction=True)
class TestDropdownInteractions:
    def test_dropdown_opens_from_list(self, list_page: InfiniteScrollingListPage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(
            name='Dropdown Test',
            description='Dropdown Description'
        )

        list_page.goto_page()

        first_item = list_page.items.first
        dropdown = EllipsisDropdown(first_item)

        assert dropdown.trigger.is_visible()

        dropdown.open()

        assert dropdown.is_open()

    def test_dropdown_has_actions(self, list_page: InfiniteScrollingListPage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(
            name='Actions Test',
            description='Actions Description'
        )

        list_page.goto_page()

        first_item = list_page.items.first
        dropdown = EllipsisDropdown(first_item)

        dropdown.open()

        assert dropdown.has_view_option()
        assert dropdown.has_edit_option()
        assert dropdown.has_delete_option()

    def test_dropdown_opens_from_table(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(
            name='Table Dropdown Test',
            description='Table Description'
        )

        table_page.goto_page()

        first_row = table_page.rows.first
        dropdown = EllipsisDropdown(first_row)

        assert dropdown.trigger.is_visible()

        dropdown.open()

        assert dropdown.is_open()
