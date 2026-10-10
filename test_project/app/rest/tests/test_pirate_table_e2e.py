from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from django.urls import reverse
from playwright.sync_api import expect

from django_spire.testing.playwright.components.scroll_component import ScrollComponent

from test_project.app.rest.tests.factories import create_test_pirate

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page

    from test_project.app.rest.models import Pirate


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

ROW_SELECTOR = 'tbody tr[data-scroll-key]'
NAME_SELECTOR = 'td:first-child a'


def _create_crew(count: int) -> list[Pirate]:
    return [
        create_test_pirate(
            first_name='Mate',
            last_name=f'Crew {number:02d}',
        )
        for number in range(1, count + 1)
    ]


def test_scrolling_a_server_rendered_table_appends_every_batch_in_order(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    crew = _create_crew(60)

    demo = demo_start()
    demo.goto('rest:page:table')

    scroll = ScrollComponent(page, row_selector=ROW_SELECTOR)
    scroll.scroll_until_row_count(60)
    state = scroll.state()

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [pirate.name for pirate in crew]
    assert state['loadedCount'] == 60
    assert state['hasMore'] is False
    assert state['items'] == []
    assert scroll.rows.first.locator(NAME_SELECTOR).get_attribute('href') == reverse(
        'rest:page:detail',
        kwargs={'pk': crew[0].pk},
    )


def test_searching_reloads_the_list_with_the_matching_rows(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    crew = _create_crew(30)
    needles = [
        create_test_pirate(first_name='Sharp', last_name='Needle Alpha'),
        create_test_pirate(first_name='Sharp', last_name='Needle Bravo'),
    ]

    demo = demo_start()
    demo.goto('rest:page:table')

    scroll = ScrollComponent(page, row_selector=ROW_SELECTOR)
    scroll.rows.first.wait_for()
    scroll.wait_until_idle()
    search = page.get_by_placeholder('Search pirates ...')

    search.fill('needle')
    scroll.wait_for_row_count(2)
    scroll.wait_until_idle()

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [
        pirate.name for pirate in needles
    ]
    assert scroll.state()['hasMore'] is False
    expect(search).to_have_value('needle')

    search.fill('')
    scroll.scroll_until_row_count(32)

    assert scroll.rows.locator(NAME_SELECTOR).all_inner_texts() == [
        pirate.name for pirate in [*crew, *needles]
    ]
    assert scroll.state()['hasMore'] is False
