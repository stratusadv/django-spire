from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from django.urls import reverse

from django_spire.testing.playwright.components.scroll_component import ScrollComponent

from test_project.app.history.tests.factories import create_test_history_example

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

ROW_SELECTOR = '[data-history-row]'
NAME_SELECTOR = '[data-history-name]'


def test_scrolling_a_read_only_list_of_dict_rows_shows_every_row_in_order(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    histories = [
        create_test_history_example(name=f'History {number:02d}', description=f'Note {number}')
        for number in range(1, 61)
    ]

    demo = demo_start()
    demo.goto('history:list_component')

    scroll = ScrollComponent(page, row_selector=ROW_SELECTOR)
    scroll.scroll_until_row_count(60)
    state = scroll.state()

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [
        history.name for history in histories
    ]
    assert state['items'][0] == {
        'pk': histories[0].pk,
        'name': 'History 01',
        'description': 'Note 1',
    }
    assert state['loadedCount'] == 60
    assert state['hasMore'] is False
    assert scroll.rows.first.locator(NAME_SELECTOR).get_attribute('href') == reverse(
        'history:detail',
        kwargs={'pk': histories[0].pk},
    )
    assert scroll.rows.first.locator('button').count() == 0


def test_a_plain_queryset_scroll_has_no_create_edit_or_delete(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    create_test_history_example(name='History 01')

    demo = demo_start()
    demo.goto('history:list_component')

    scroll = ScrollComponent(page, row_selector=ROW_SELECTOR)
    scroll.wait_for_row_count(1)
    scroll.wait_until_idle()

    available = page.evaluate(f"""
        () => {{
            const scroll = {scroll.data_expression}

            return {{
                helpers: ['createItem', 'editItem', 'deleteItem'].filter(name => name in scroll),
                callables: ['load_item_form', 'load_item_delete_confirmation'].filter(
                    name => typeof scroll.component[name] === 'function'
                ),
                rowOperations: ['addItem', 'refreshItem', 'removeItem', 'reloadItems'].filter(
                    name => typeof scroll[name] === 'function'
                ),
            }}
        }}
    """)

    assert available == {
        'helpers': [],
        'callables': [],
        'rowOperations': ['addItem', 'refreshItem', 'removeItem', 'reloadItems'],
    }
