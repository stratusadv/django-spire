from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from django.urls import reverse

from django_spire.testing.playwright.components.glue_scroll import GlueScroll

from test_project.app.comment.models import CommentExample
from test_project.app.comment.tests.factories import create_test_comment_example

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page, Route


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

ROW_SELECTOR = '.row.border-bottom'

SCROLL = """
    [...document.querySelectorAll('[x-data]')]
        .map(element => Alpine.$data(element))
        .find(data => data && 'loadGeneration' in data && 'rendersRows' in data)
"""

SCROLL_STATE = f"""
    () => {{
        const scroll = {SCROLL}

        return {{
            names: scroll.items.map(item => item.name),
            hasMore: scroll.hasMore,
            isLoading: scroll.isLoading,
            loadedCount: scroll.loadedCount,
        }}
    }}
"""

SCROLL_IS_IDLE = f'() => !({SCROLL}).isLoading'


def _create_comments(count: int) -> list[str]:
    names = [f'Comment {number:02d}' for number in range(1, count + 1)]

    for name in names:
        create_test_comment_example(name=name)

    return names


def _scroll_until_row_count(page: Page, scroll: GlueScroll, count: int) -> None:
    scroll.wait_for_rows()
    shown = scroll.row_count()

    while shown < count:
        scroll.scroll_to_bottom()
        scroll.wait_for_row_count_to_increase(shown)
        shown = scroll.row_count()

    page.wait_for_function(SCROLL_IS_IDLE)


def test_scrolling_appends_every_batch_once_and_in_order(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    names = _create_comments(60)

    demo = demo_start()
    demo.goto('comment:page:list2')

    scroll = GlueScroll(page, row_selector=ROW_SELECTOR)
    _scroll_until_row_count(page, scroll, 60)

    scroll.scroll_to_bottom()
    page.wait_for_function(SCROLL_IS_IDLE)
    state = page.evaluate(SCROLL_STATE)

    assert state['names'] == names
    assert state['loadedCount'] == 60
    assert state['hasMore'] is False
    assert scroll.row_count() == 60


def test_reloading_shows_the_current_first_batch(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    names = _create_comments(30)

    demo = demo_start()
    demo.goto('comment:page:list2')

    scroll = GlueScroll(page, row_selector=ROW_SELECTOR)
    _scroll_until_row_count(page, scroll, 30)

    CommentExample.objects.filter(name=names[0]).delete()

    state = page.evaluate(f"""
        async () => {{
            await ({SCROLL}).reloadItems()

            return ({SCROLL_STATE})()
        }}
    """)

    assert state['names'] == names[1:26]
    assert names[0] not in state['names']
    assert state['loadedCount'] == 25
    assert state['hasMore'] is True
    assert state['isLoading'] is False


def test_a_batch_in_flight_when_a_reload_begins_is_never_shown(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    names = _create_comments(60)

    demo = demo_start()
    demo.goto('comment:page:list2')

    scroll = GlueScroll(page, row_selector=ROW_SELECTOR)
    scroll.wait_for_rows()
    page.wait_for_function(SCROLL_IS_IDLE)

    held_routes: list[Route] = []

    def hold_load_items(route: Route) -> None:
        if 'load_items' in (route.request.post_data or ''):
            held_routes.append(route)
        else:
            route.continue_()

    page.route('**/__dg__/**', hold_load_items)

    held_batch_first_name = page.evaluate(f"""
        (names) => {{
            const scroll = {SCROLL}
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

    for _ in range(100):
        if held_routes:
            break
        page.wait_for_timeout(50)

    assert len(held_routes) == 1
    assert held_batch_first_name in names[25:]

    page.evaluate(f'() => {{ window.heldReload = ({SCROLL}).reloadItems() }}')
    held_routes[0].continue_()
    page.unroute('**/__dg__/**', hold_load_items)

    state = page.evaluate(f"""
        async () => {{
            await Promise.all([window.heldLoad, window.heldReload])

            return {{...({SCROLL_STATE})(), heldBatchWasShown: window.heldBatchWasShown}}
        }}
    """)

    assert state['heldBatchWasShown'] is False
    assert state['names'] == names[:25]
    assert state['loadedCount'] == 25
    assert state['isLoading'] is False
    assert state['hasMore'] is True


def test_a_viewport_taller_than_the_list_still_loads_every_batch(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    names = _create_comments(60)

    demo = demo_start()
    page.set_viewport_size({'width': 1280, 'height': 6000})
    demo.goto('comment:page:list2')

    scroll = GlueScroll(page, row_selector=ROW_SELECTOR)
    scroll.wait_for_row_count(60)
    page.wait_for_function(SCROLL_IS_IDLE)
    state = page.evaluate(SCROLL_STATE)

    assert state['names'] == names
    assert state['loadedCount'] == 60
    assert state['hasMore'] is False


def test_creating_and_editing_go_to_the_one_form_route(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    _create_comments(2)
    first_comment = CommentExample.objects.order_by('id').first()

    demo = demo_start()
    demo.goto('comment:page:list2')

    scroll = GlueScroll(page, row_selector=ROW_SELECTOR)
    scroll.wait_for_row_count(2)
    page.wait_for_function(SCROLL_IS_IDLE)
    page.route(
        '**/comment/page/*/form/',
        lambda route: route.fulfill(status=200, content_type='text/html', body='Comment form'),
    )

    page.get_by_role('button', name='New Comment').click()
    page.wait_for_url(f'**{reverse("comment:page:form", kwargs={"pk": 0})}')
    page.go_back()
    scroll.wait_for_row_count(2)
    page.wait_for_function(SCROLL_IS_IDLE)

    scroll.rows.first.get_by_title('Edit Comment').click()
    page.wait_for_url(f'**{reverse("comment:page:form", kwargs={"pk": first_comment.pk})}')
