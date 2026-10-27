from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

SCROLL_CONTAINER = '[data-side-navigation-scroll]'
TOGGLE = r'[x-data="sideNavigation()"] [\@click="toggle_collapse()"]'
SHORT_VIEWPORT = {'width': 1280, 'height': 400}
PHONE_VIEWPORT = {'width': 400, 'height': 800}
LINK_COLOR = 'rgb(1, 2, 3)'


def open_home(page: Page, demo_start: Callable[..., Demo]) -> None:
    demo_start().goto('home:page:home')
    page.wait_for_function('() => window.Alpine !== undefined')


def test_collapsing_stays_collapsed_after_a_reload(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    open_home(page, demo_start)
    page.locator(TOGGLE).click()

    expect(page.locator('html')).to_have_class(r'side-nav-collapsed')

    page.reload()

    expect(page.locator('html')).to_have_class(r'side-nav-collapsed')
    expect(page.locator(f'{TOGGLE} .bi-chevron-right')).to_be_visible()


def test_expanding_stays_expanded_after_a_reload(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    open_home(page, demo_start)
    page.locator(TOGGLE).click()
    page.reload()
    page.locator(TOGGLE).click()

    expect(page.locator('html')).not_to_have_class(r'side-nav-collapsed')

    page.reload()

    expect(page.locator('html')).not_to_have_class(r'side-nav-collapsed')
    expect(page.locator(f'{TOGGLE} .bi-chevron-left')).to_be_visible()


def test_scroll_position_is_restored_after_a_reload(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    page.set_viewport_size(SHORT_VIEWPORT)
    open_home(page, demo_start)

    container = page.locator(SCROLL_CONTAINER)
    container.evaluate('(element) => { element.scrollTop = 100 }')
    page.wait_for_function("() => localStorage.getItem('side_nav_scroll') === '100'")

    page.reload()

    # Chrome's scroll anchoring moves it a few pixels as the icon font loads.
    assert abs(container.evaluate('(element) => element.scrollTop') - 100) <= 10


def test_fades_show_which_way_the_navigation_can_scroll(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    page.set_viewport_size(SHORT_VIEWPORT)
    open_home(page, demo_start)

    top_fade = page.locator('.side-navigation-fade-top')
    bottom_fade = page.locator('.side-navigation-fade-bottom')

    expect(top_fade).to_be_hidden()
    expect(bottom_fade).to_be_visible()

    page.locator(SCROLL_CONTAINER).evaluate(
        '(element) => { element.scrollTop = element.scrollHeight }'
    )

    expect(top_fade).to_be_visible()
    expect(bottom_fade).to_be_hidden()


def test_the_mobile_menu_header_takes_the_side_navigation_link_color(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    page.set_viewport_size(PHONE_VIEWPORT)
    open_home(page, demo_start)

    # The default theme's link color is its primary, so a distinct one tells the two apart.
    page.add_style_tag(content=f':root {{ --side-navigation-link-color: {LINK_COLOR} !important; }}')
    page.locator('.d-lg-none .bi-list').click()

    header = page.locator('.side-navigation-mobile-header')

    for icon in ('.bi-search', '.bi-bell-fill', '.bi-person-circle'):
        expect(header.locator(icon)).to_have_css('color', LINK_COLOR)

    header.locator('.bi-person-circle').click()

    expect(header.get_by_role('link', name='Logout')).to_be_visible()
