from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from test_project.apps.lazy_tabs.tests.test_playwright.pages.demo_page import LazyTabsDemoPage


@pytest.mark.django_db(transaction=True)
class TestDemoPage:
    def test_demo_page_loads(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()

        assert demo_page.page.locator('h1').inner_text().__contains__('Lazy Tabs')

    def test_demo_first_tab_selected_by_default(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(0)
        assert not demo_page.is_demo_tab_selected(1)
        assert not demo_page.is_demo_tab_selected(2)

    def test_demo_first_tab_content_loads(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        section_text = demo_page.get_demo_visible_section_text()
        assert 'Overview' in section_text

    def test_demo_clicking_tab_changes_selection(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(1)
        demo_page.page.wait_for_timeout(500)

        assert not demo_page.is_demo_tab_selected(0)
        assert demo_page.is_demo_tab_selected(1)

    def test_demo_clicking_tab_loads_content(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(1)
        demo_page.page.wait_for_timeout(500)

        section_text = demo_page.get_demo_visible_section_text()
        assert 'Details' in section_text

    def test_demo_url_updates_on_tab_change(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(2)
        demo_page.page.wait_for_timeout(200)

        assert demo_page.get_url_param('demo_tab') == '3'

    def test_demo_tab_from_url_param(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto(f'{demo_page.url}?demo_tab=2')
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(1)

    def test_demo_tab_content_cached(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(1)
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(0)
        demo_page.page.wait_for_timeout(100)

        section_text = demo_page.get_demo_visible_section_text()
        assert 'Overview' in section_text

    def test_demo_all_tabs_accessible(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()

        assert demo_page.demo_tab_triggers.count() == 3
        assert demo_page.demo_tab_sections.count() == 3

    def test_demo_third_tab_loads_settings(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(2)
        demo_page.page.wait_for_timeout(500)

        section_text = demo_page.get_demo_visible_section_text()
        assert 'Settings' in section_text


@pytest.mark.django_db(transaction=True)
class TestUserTabs:
    def test_user_first_tab_selected_by_default(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_user_tab_selected(0)
        assert not demo_page.is_user_tab_selected(1)

    def test_user_first_tab_content_loads(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        section_text = demo_page.get_user_visible_section_text()
        assert 'Profile' in section_text

    def test_user_clicking_tab_changes_selection(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_user_tab(1)
        demo_page.page.wait_for_timeout(500)

        assert not demo_page.is_user_tab_selected(0)
        assert demo_page.is_user_tab_selected(1)

    def test_user_clicking_tab_loads_content(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_user_tab(1)
        demo_page.page.wait_for_timeout(500)

        section_text = demo_page.get_user_visible_section_text()
        assert 'Activity' in section_text

    def test_user_url_updates_on_tab_change(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_user_tab(1)
        demo_page.page.wait_for_timeout(200)

        assert demo_page.get_url_param('user_tab') == '2'

    def test_user_all_tabs_accessible(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()

        assert demo_page.user_tab_triggers.count() == 2
        assert demo_page.user_tab_sections.count() == 2


@pytest.mark.django_db(transaction=True)
class TestMultipleTabComponents:
    def test_both_components_load_first_tab(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(0)
        assert demo_page.is_user_tab_selected(0)

        demo_section = demo_page.get_demo_visible_section_text()
        user_section = demo_page.get_user_visible_section_text()

        assert 'Overview' in demo_section
        assert 'Profile' in user_section

    def test_components_independent_selection(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(2)
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(2)
        assert demo_page.is_user_tab_selected(0)

    def test_components_independent_url_params(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(2)
        demo_page.page.wait_for_timeout(200)

        demo_page.click_user_tab(1)
        demo_page.page.wait_for_timeout(200)

        assert demo_page.get_url_param('demo_tab') == '3'
        assert demo_page.get_url_param('user_tab') == '2'

    def test_url_params_restore_both_components(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto(f'{demo_page.url}?demo_tab=3&user_tab=2')
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(2)
        assert demo_page.is_user_tab_selected(1)

    def test_clicking_one_does_not_affect_other(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_user_tab(1)
        demo_page.page.wait_for_timeout(500)

        demo_section = demo_page.get_demo_visible_section_text()
        assert 'Overview' in demo_section

        assert demo_page.is_demo_tab_selected(0)

    def test_rapid_switching_between_components(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(1)
        demo_page.page.wait_for_timeout(100)

        demo_page.click_user_tab(1)
        demo_page.page.wait_for_timeout(100)

        demo_page.click_demo_tab(2)
        demo_page.page.wait_for_timeout(100)

        demo_page.click_user_tab(0)
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(2)
        assert demo_page.is_user_tab_selected(0)


@pytest.mark.django_db(transaction=True)
class TestKeyboardNavigation:
    def test_arrow_right_moves_to_next_tab(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.get_demo_tab_trigger(0).focus()
        demo_page.page.keyboard.press('ArrowRight')
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(1)

    def test_arrow_left_moves_to_previous_tab(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(2)
        demo_page.page.wait_for_timeout(500)

        demo_page.get_demo_tab_trigger(2).focus()
        demo_page.page.keyboard.press('ArrowLeft')
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(1)

    def test_home_moves_to_first_tab(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(2)
        demo_page.page.wait_for_timeout(500)

        demo_page.get_demo_tab_trigger(2).focus()
        demo_page.page.keyboard.press('Home')
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(0)

    def test_end_moves_to_last_tab(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.get_demo_tab_trigger(0).focus()
        demo_page.page.keyboard.press('End')
        demo_page.page.wait_for_timeout(500)

        assert demo_page.is_demo_tab_selected(2)


@pytest.mark.django_db(transaction=True)
class TestTabCaching:
    def test_tab_content_not_refetched(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(1)
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(0)
        demo_page.page.wait_for_timeout(100)

        demo_page.click_demo_tab(1)
        demo_page.page.wait_for_timeout(100)

        section_text = demo_page.get_demo_visible_section_text()
        assert 'Details' in section_text

    def test_all_tabs_can_be_loaded(self, demo_page: LazyTabsDemoPage) -> None:
        demo_page.goto_page()
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(1)
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(2)
        demo_page.page.wait_for_timeout(500)

        demo_page.click_demo_tab(0)
        demo_page.page.wait_for_timeout(100)

        assert 'Overview' in demo_page.get_demo_visible_section_text()

        demo_page.click_demo_tab(1)
        demo_page.page.wait_for_timeout(100)

        assert 'Details' in demo_page.get_demo_visible_section_text()

        demo_page.click_demo_tab(2)
        demo_page.page.wait_for_timeout(100)

        assert 'Settings' in demo_page.get_demo_visible_section_text()
