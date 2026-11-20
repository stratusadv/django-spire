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
NAVIGATION_LINK = 'a[x-bind="sideNavigationLink"][href^="/"]'
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


def test_the_active_link_follows_the_side_navigation_path(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    open_home(page, demo_start)

    href = page.locator(f'{SCROLL_CONTAINER} {NAVIGATION_LINK}:not(.active)').first.get_attribute('href')
    link = page.locator(f'{SCROLL_CONTAINER} a[href="{href}"]')

    page.locator('[x-data="sideNavigation()"]').evaluate(
        '(element, path) => { Alpine.$data(element).current_path = path }', href
    )

    expect(link).to_contain_class('active')
    expect(page.locator(f'{SCROLL_CONTAINER} {NAVIGATION_LINK}.active')).to_have_count(1)


def test_a_link_loads_its_page_once(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    open_home(page, demo_start)

    link = page.locator(f'{SCROLL_CONTAINER} {NAVIGATION_LINK}:not(.active)').first
    href = link.get_attribute('href')

    requests = []
    page.on('request', lambda request: requests.append(request) if request.url.endswith(href) else None)

    with page.expect_navigation():
        link.click()

    assert page.url.endswith(href)
    assert len(requests) == 1


def test_a_modified_click_opens_the_link_in_a_new_tab(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    open_home(page, demo_start)
    url = page.url

    link = page.locator(f'{SCROLL_CONTAINER} {NAVIGATION_LINK}:not(.active)').first
    href = link.get_attribute('href')

    with page.context.expect_page() as new_tab:
        link.click(modifiers=['ControlOrMeta'])

    new_tab.value.wait_for_load_state()

    assert new_tab.value.url.endswith(href)
    assert page.url == url


def test_the_mobile_menu_opens_and_closes_the_side_navigation(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    page.set_viewport_size(PHONE_VIEWPORT)
    open_home(page, demo_start)

    navigation = page.locator('.side-navigation-drawer')
    expect(navigation).to_be_hidden()

    page.locator('.d-lg-none .bi-list').click()

    expect(navigation).to_be_visible()
    expect(navigation.locator(SCROLL_CONTAINER).locator('a').first).to_be_visible()
    expect(navigation.locator('.side-navigation-mobile-header + *')).to_be_hidden()
    expect(page.locator('body')).to_have_css('overflow', 'hidden')

    navigation.locator('.side-navigation-mobile-header .bi-x-lg').click()

    expect(navigation).to_be_hidden()
    expect(page.locator('body')).not_to_have_css('overflow', 'hidden')


def test_the_mobile_menu_shows_labels_when_the_side_navigation_is_collapsed(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    open_home(page, demo_start)
    page.locator(TOGGLE).click()

    page.set_viewport_size(PHONE_VIEWPORT)
    page.reload()
    page.locator('.d-lg-none .bi-list').click()

    label = page.locator(f'{SCROLL_CONTAINER} .side-nav-expanded-only').first
    expect(label).to_be_visible()
    expect(page.locator(TOGGLE)).to_be_hidden()


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

    # The account menu is a dropdown on its own surface, not a side navigation link.
    for name in ('Change Password', 'Logout'):
        link = header.get_by_role('link', name=name)
        expect(link).to_be_visible()
        expect(link).not_to_have_css('color', LINK_COLOR)
