from __future__ import annotations

import re

import pytest

from typing import TYPE_CHECKING
from urllib.parse import quote

from django.urls import reverse
from playwright.sync_api import expect

from django_spire.testing.playwright.components.scroll_component import ScrollComponent

from test_project.app.ordering.models import Duck
from test_project.app.ordering.tests.factories import create_test_duck

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Locator, Page, Route


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

ROW_SELECTOR = '[data-scroll-key]'
NAME_SELECTOR = '[data-duck-name]'
COLOR_SELECTOR = '[data-duck-color]'


def _open_duck_list(page: Page, demo_start: Callable[..., Demo], row_count: int) -> ScrollComponent:
    demo = demo_start()
    demo.goto('order:list_component')

    scroll = ScrollComponent(page, row_selector=ROW_SELECTOR)
    scroll.wait_for_row_count(row_count)
    scroll.wait_until_idle()

    return scroll


def _row(page: Page, duck: Duck) -> Locator:
    return page.locator(f"[data-scroll-key='{duck.pk}']")


def test_repainting_a_duck_rerenders_its_row_and_leaves_the_others_in_place(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_duck(name='Alpha Duck', color='#111111', order=1)
    bravo = create_test_duck(name='Bravo Duck', color='#222222', order=2)

    scroll = _open_duck_list(page, demo_start, row_count=2)

    _row(page, bravo).evaluate("row => { row.dataset.untouched = 'yes' }")
    _row(page, alpha).get_by_label('Duck colour').fill('#00ff00')

    expect(_row(page, alpha).locator(COLOR_SELECTOR)).to_have_text('#00ff00')
    expect(_row(page, bravo)).to_have_attribute('data-untouched', 'yes')
    expect(_row(page, bravo).locator(COLOR_SELECTOR)).to_have_text('#222222')

    assert scroll.row_count() == 2
    assert Duck.objects.get(pk=alpha.pk).color == '#00ff00'


def test_duplicating_a_duck_adds_the_copy_to_the_top_of_the_list(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    create_test_duck(name='Alpha Duck', order=1)
    bravo = create_test_duck(name='Bravo Duck', order=2)

    scroll = _open_duck_list(page, demo_start, row_count=2)

    _row(page, bravo).get_by_title('Duplicate Duck').click()
    scroll.wait_for_row_count(3)

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [
        'Bravo Duck (Copy)',
        'Alpha Duck',
        'Bravo Duck',
    ]
    assert scroll.state()['loadedCount'] == 3


def test_deleting_a_duck_is_confirmed_and_uses_the_overridden_delete(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_duck(name='Alpha Duck', order=1)
    bravo = create_test_duck(name='Bravo Duck', order=2)

    scroll = _open_duck_list(page, demo_start, row_count=2)
    modal = page.locator('#baseDispatchModal')

    _row(page, alpha).get_by_title('Delete Duck').click()
    expect(modal).to_contain_text('Alpha Duck')

    requests_while_cancelling: list[str] = []
    page.on('request', lambda request: requests_while_cancelling.append(request.url))
    modal.get_by_role('button', name='Cancel').click()
    expect(modal).to_be_hidden()

    assert requests_while_cancelling == []

    assert scroll.row_count() == 2
    assert Duck.objects.get(pk=alpha.pk).is_active is True

    _row(page, alpha).get_by_title('Delete Duck').click()
    modal.get_by_role('button', name='Delete').click()
    scroll.wait_for_row_count(1)

    expect(modal).to_be_hidden()
    expect(_row(page, bravo)).to_be_visible()

    deleted = Duck.objects.get(pk=alpha.pk)

    assert deleted.is_active is False
    assert deleted.is_deleted is False


def test_confirming_twice_in_quick_succession_sends_one_request(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_duck(name='Alpha Duck', order=1)
    create_test_duck(name='Bravo Duck', order=2)

    scroll = _open_duck_list(page, demo_start, row_count=2)
    modal = page.locator('#baseDispatchModal')

    _row(page, alpha).get_by_title('Delete Duck').click()
    expect(modal).to_contain_text('Alpha Duck')

    confirm_requests: list[str] = []
    page.on(
        'request',
        lambda request: confirm_requests.append(request.url)
        if '"confirm"' in (request.post_data or '') else None,
    )

    modal.get_by_role('button', name='Delete').evaluate(
        'button => { button.click(); button.click() }'
    )
    scroll.wait_for_row_count(1)

    expect(modal).to_be_hidden()

    assert len(confirm_requests) == 1


def test_both_buttons_are_off_while_a_confirmation_is_in_flight(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_duck(name='Alpha Duck', order=1)
    create_test_duck(name='Bravo Duck', order=2)

    scroll = _open_duck_list(page, demo_start, row_count=2)
    modal = page.locator('#baseDispatchModal')

    _row(page, alpha).get_by_title('Delete Duck').click()
    expect(modal).to_contain_text('Alpha Duck')

    held_routes: list[Route] = []

    def hold_confirm(route: Route) -> None:
        if '"confirm"' in (route.request.post_data or ''):
            held_routes.append(route)
        else:
            route.continue_()

    page.route('**/__dg__/**', hold_confirm)

    cancel_button = modal.get_by_role('button', name='Cancel')
    delete_button = modal.get_by_role('button', name='Delete')
    delete_button.click()

    expect(delete_button).to_be_disabled()
    expect(cancel_button).to_be_disabled()
    expect(delete_button.locator('.spinner-border')).to_be_visible()
    expect(cancel_button.locator('.spinner-border')).to_be_hidden()

    assert len(held_routes) == 1

    held_routes[0].continue_()
    scroll.wait_for_row_count(1)

    expect(modal).to_be_hidden()


@pytest.mark.console_error_expected('status of 500')
def test_a_confirmation_that_fails_can_be_tried_again(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_duck(name='Alpha Duck', order=1)

    scroll = _open_duck_list(page, demo_start, row_count=1)
    modal = page.locator('#baseDispatchModal')

    _row(page, alpha).get_by_title('Delete Duck').click()
    expect(modal).to_contain_text('Alpha Duck')

    def fail_confirm(route: Route) -> None:
        if '"confirm"' in (route.request.post_data or ''):
            route.fulfill(status=500, body='')
        else:
            route.continue_()

    page.route('**/__dg__/**', fail_confirm)
    page.evaluate("""
        () => window.addEventListener('unhandledrejection', event => {
            window.rejectedWith = event.reason?.name
            event.preventDefault()
        })
    """)

    delete_button = modal.get_by_role('button', name='Delete')

    with page.expect_response('**/__dg__/**'):
        delete_button.click()

    expect(delete_button).to_be_enabled()
    expect(modal.get_by_role('button', name='Cancel')).to_be_enabled()
    expect(modal).to_be_visible()

    assert page.evaluate('() => window.rejectedWith') == 'GlueHttpError'
    expect(page.get_by_text('Something went wrong. Please try again.')).to_be_visible()

    page.unroute('**/__dg__/**', fail_confirm)
    delete_button.click()
    scroll.wait_for_row_count(0)

    expect(modal).to_be_hidden()


def test_creating_and_editing_go_to_their_own_pages(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    alpha = create_test_duck(name='Alpha Duck', order=1)

    _open_duck_list(page, demo_start, row_count=1)

    returning_to_the_list = r'\?return_url=' + re.escape(
        quote(reverse('order:list_component'), safe='')
    )

    page.get_by_role('button', name='Add Duck').click()
    page.wait_for_url(re.compile(re.escape(reverse('order:create')) + returning_to_the_list))
    page.go_back()

    _row(page, alpha).get_by_title('Edit Duck').click()
    page.wait_for_url(re.compile(
        re.escape(reverse('order:update', kwargs={'pk': alpha.pk})) + returning_to_the_list
    ))


def test_searching_reloads_the_list_with_the_matching_ducks(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    create_test_duck(name='Alpha Duck', order=1)
    create_test_duck(name='Needle Duck', order=2)
    create_test_duck(name='Charlie Duck', order=3)

    scroll = _open_duck_list(page, demo_start, row_count=3)

    page.get_by_placeholder('Search ducks ...').fill('needle')
    scroll.wait_for_row_count(1)
    scroll.wait_until_idle()

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == ['Needle Duck']
