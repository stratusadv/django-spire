from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from test_project.apps.infinite_scrolling.models import InfiniteScrolling

if TYPE_CHECKING:
    from test_project.apps.infinite_scrolling.tests.test_playwright.pages.table_page import InfiniteScrollingTablePage


@pytest.mark.django_db(transaction=True)
class TestTablePage:
    def test_table_page_loads(self, table_page: InfiniteScrollingTablePage) -> None:
        table_page.goto_page()

        assert table_page.page.locator('h1').inner_text().__contains__('Infinite Scrolling')
        assert table_page.table.is_visible()

    def test_table_headers_visible(self, table_page: InfiniteScrollingTablePage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        table_page.goto_page()

        assert table_page.get_header('Name').is_visible()
        assert table_page.get_header('Description').is_visible()
        assert table_page.get_header('Created').is_visible()
        assert table_page.get_header('Actions').is_visible()

    def test_table_sorting_name_ascending(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(name='Zebra', description='Last')
        InfiniteScrolling.objects.create(name='Apple', description='First')
        InfiniteScrolling.objects.create(name='Banana', description='Second')

        table_page.goto_page()
        table_page.click_header('Name')
        table_page.page.wait_for_timeout(800)

        assert 'Apple' in table_page.get_first_row_text()

    def test_table_sorting_name_descending(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(name='Zebra', description='Last')
        InfiniteScrolling.objects.create(name='Apple', description='First')
        InfiniteScrolling.objects.create(name='Banana', description='Second')

        table_page.goto_page()
        table_page.click_header('Name')
        table_page.page.wait_for_timeout(800)

        table_page.click_header('Name')
        table_page.page.wait_for_timeout(800)

        assert 'Zebra' in table_page.get_first_row_text()

    def test_table_sorting_toggles_icon(self, table_page: InfiniteScrollingTablePage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        table_page.goto_page()

        table_page.click_header('Name')
        table_page.page.wait_for_timeout(500)
        assert table_page.is_sorted_ascending('Name')

        table_page.click_header('Name')
        table_page.page.wait_for_timeout(500)
        assert table_page.is_sorted_descending('Name')

    def test_table_infinite_scroll(self, table_page: InfiniteScrollingTablePage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        table_page.goto_page()

        initial_count = table_page.get_loaded_count()

        table_page.scroll_to_bottom()
        table_page.wait_for_count_to_increase(initial_count)

        final_count = table_page.get_loaded_count()
        assert final_count > initial_count

    def test_row_count_display(self, table_page: InfiniteScrollingTablePage, infinite_scrolling_data: list[InfiniteScrolling]) -> None:
        table_page.goto_page()

        footer_text = table_page.page.locator('.fs-7.text-app-secondary').first.inner_text()
        assert 'Showing' in footer_text
        assert 'of' in footer_text
        assert 'rows' in footer_text


@pytest.mark.django_db(transaction=True)
class TestRowSelection:
    def test_select_single_row(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(name='Test Item 1', description='Desc 1')
        InfiniteScrolling.objects.create(name='Test Item 2', description='Desc 2')

        table_page.goto_page()
        table_page.select_row(0)
        table_page.page.wait_for_timeout(200)

        assert table_page.get_selected_count() == 1

    def test_select_multiple_rows(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(name='Test Item 1', description='Desc 1')
        InfiniteScrolling.objects.create(name='Test Item 2', description='Desc 2')
        InfiniteScrolling.objects.create(name='Test Item 3', description='Desc 3')

        table_page.goto_page()

        table_page.select_row(0)
        table_page.page.wait_for_timeout(200)

        table_page.select_row(2)
        table_page.page.wait_for_timeout(200)

        assert table_page.get_selected_count() == 2

    def test_deselect_row(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(name='Test Item 1', description='Desc 1')

        table_page.goto_page()

        table_page.select_row(0)
        table_page.page.wait_for_timeout(200)

        table_page.deselect_row(0)
        table_page.page.wait_for_timeout(200)

        assert not table_page.selected_count_text.is_visible()

    def test_select_all_rows(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(name='Test Item 1', description='Desc 1')
        InfiniteScrolling.objects.create(name='Test Item 2', description='Desc 2')
        InfiniteScrolling.objects.create(name='Test Item 3', description='Desc 3')

        table_page.goto_page()

        table_page.select_all_rows()
        table_page.page.wait_for_timeout(200)

        assert table_page.get_selected_count() == 3

    def test_deselect_all_rows(self, table_page: InfiniteScrollingTablePage, transactional_db: None) -> None:
        InfiniteScrolling.objects.create(name='Test Item 1', description='Desc 1')
        InfiniteScrolling.objects.create(name='Test Item 2', description='Desc 2')

        table_page.goto_page()

        table_page.select_all_rows()
        table_page.page.wait_for_timeout(200)

        table_page.deselect_all_rows()
        table_page.page.wait_for_timeout(200)

        assert not table_page.selected_count_text.is_visible()
