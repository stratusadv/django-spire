from __future__ import annotations

import re

import pytest

from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from django.urls import reverse

from django_spire.testing.playwright.components.scroll_component import ScrollComponent

from test_project.app.comment.models import CommentExample
from test_project.app.comment.tests.factories import create_test_comment_example

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page, Route


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

ROW_SELECTOR = '.row.border-bottom'


def _create_comments(count: int) -> list[str]:
    names = [f'Comment {number:02d}' for number in range(1, count + 1)]

    for name in names:
        create_test_comment_example(name=name)

    return names


def _open_comment_list(page: Page, demo_start: Callable[..., Demo]) -> ScrollComponent:
    demo = demo_start()
    demo.goto('comment:page:list_component')

    scroll = ScrollComponent(page, row_selector=ROW_SELECTOR)
    scroll.rows.first.wait_for()
    scroll.wait_until_idle()

    return scroll


def _names(state: dict[str, Any]) -> list[str]:
    return [item['name'] for item in state['items']]


def test_scrolling_appends_every_batch_once_and_in_order(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    names = _create_comments(60)

    scroll = _open_comment_list(page, demo_start)
    scroll.scroll_until_row_count(60)
    scroll.scroll_to_bottom()
    scroll.wait_until_idle()
    state = scroll.state()

    assert _names(state) == names
    assert state['loadedCount'] == 60
    assert state['hasMore'] is False
    assert scroll.row_count() == 60


def test_reloading_shows_the_current_first_batch(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    names = _create_comments(30)

    scroll = _open_comment_list(page, demo_start)
    scroll.scroll_until_row_count(30)

    CommentExample.objects.filter(name=names[0]).delete()

    state = scroll.reload_items()

    assert _names(state) == names[1:26]
    assert state['loadedCount'] == 25
    assert state['hasMore'] is True
    assert state['isLoading'] is False


def test_a_batch_in_flight_when_a_reload_begins_is_never_shown(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    names = _create_comments(60)

    scroll = _open_comment_list(page, demo_start)

    held_routes: list[Route] = []

    def hold_load_items(route: Route) -> None:
        if 'load_items' in (route.request.post_data or ''):
            held_routes.append(route)
        else:
            route.continue_()

    page.route('**/__dg__/**', hold_load_items)

    with page.expect_request(lambda request: 'load_items' in (request.post_data or '')):
        held_batch_first_name = page.evaluate(f"""
            (names) => {{
                const scroll = {scroll.data_expression}
                const heldBatchFirstName = names[scroll.items.length]

                window.heldBatchWasShown = false
                Alpine.effect(() => {{
                    if (scroll.items.some(item => item.name === heldBatchFirstName)) {{
                        window.heldBatchWasShown = true
                    }}
                }})
                window.heldLoad = scroll.loadMoreItems()

                return heldBatchFirstName
            }}
        """, names)

    page.evaluate(f'() => {{ window.heldReload = {scroll.data_expression}.reloadItems() }}')

    assert len(held_routes) == 1
    assert held_batch_first_name in names[25:]

    held_routes[0].continue_()
    page.unroute('**/__dg__/**', hold_load_items)

    state = page.evaluate(f"""
        async () => {{
            await Promise.all([window.heldLoad, window.heldReload])

            return {{...{scroll.state_expression}, heldBatchWasShown: window.heldBatchWasShown}}
        }}
    """)

    assert state['heldBatchWasShown'] is False
    assert _names(state) == names[:25]
    assert state['loadedCount'] == 25
    assert state['isLoading'] is False
    assert state['hasMore'] is True


def test_a_viewport_taller_than_the_list_still_loads_every_batch(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    names = _create_comments(60)

    page.set_viewport_size({'width': 1280, 'height': 6000})

    scroll = _open_comment_list(page, demo_start)
    scroll.wait_for_row_count(60)
    scroll.wait_until_idle()
    state = scroll.state()

    assert _names(state) == names
    assert state['loadedCount'] == 60
    assert state['hasMore'] is False


def test_creating_and_editing_go_to_the_one_form_route(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    _create_comments(2)
    first_comment = CommentExample.objects.order_by('id').first()

    scroll = _open_comment_list(page, demo_start)
    scroll.wait_for_row_count(2)
    page.route(
        re.compile(r'/comment/page/\d+/form/'),
        lambda route: route.fulfill(status=200, content_type='text/html', body='Comment form'),
    )
    returning_to_the_list = r'\?return_url=' + re.escape(
        quote(reverse('comment:page:list_component'), safe='')
    )

    page.get_by_role('button', name='New Comment').click()
    page.wait_for_url(re.compile(
        re.escape(reverse('comment:page:form', kwargs={'pk': 0})) + returning_to_the_list
    ))
    page.go_back()
    scroll.wait_for_row_count(2)
    scroll.wait_until_idle()

    scroll.rows.first.get_by_title('Edit Comment').click()
    page.wait_for_url(re.compile(
        re.escape(reverse('comment:page:form', kwargs={'pk': first_comment.pk}))
        + returning_to_the_list
    ))
