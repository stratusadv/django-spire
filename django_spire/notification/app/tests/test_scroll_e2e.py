from __future__ import annotations

import datetime

import pytest

from typing import TYPE_CHECKING

from django.utils.timezone import now

from django_spire.notification.app.tests.factories import create_test_app_notification

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

SEARCH_INPUT = 'input[placeholder="Search Notifications ..."]'

LOAD_MORE_DURING_SEARCH = """
    async (searchInput) => {
        const scroll = Alpine.$data(document.querySelector(searchInput).closest('[x-data]'))
        while (scroll.isLoading) await new Promise((resolve) => setTimeout(resolve, 50))
        if (!scroll.hasMore) throw new Error('the scroll must have another page to load')

        const prototype = Object.getPrototypeOf(scroll.scrollQuerySet)
        const originalLoadMore = prototype.loadMore
        let releaseLoadMore
        const loadMoreGate = new Promise((resolve) => { releaseLoadMore = resolve })

        prototype.loadMore = async function (...args) {
            await loadMoreGate
            return originalLoadMore.apply(this, args)
        }

        try {
            const loadMore = scroll.loadMoreItems()
            scroll.searchQuery = 'Notice 7'
            await new Promise((resolve) => setTimeout(resolve, 1500))
            releaseLoadMore()
            await loadMore
            await new Promise((resolve) => setTimeout(resolve, 500))
        } finally {
            prototype.loadMore = originalLoadMore
        }

        return scroll.items.map(
            (item) => item.notification?.title ?? `NULL notification on ${item.id}`,
        )
    }
"""


LOAD_EVERY_PAGE = """
    async (searchInput) => {
        const scroll = Alpine.$data(document.querySelector(searchInput).closest('[x-data]'))
        while (scroll.isLoading) await new Promise((resolve) => setTimeout(resolve, 50))

        while (scroll.hasMore) {
            await scroll.loadMoreItems()
            while (scroll.isLoading) await new Promise((resolve) => setTimeout(resolve, 50))
        }

        return scroll.items.map(
            (item) => item.notification?.title ?? `NULL notification on ${item.id}`,
        )
    }
"""


def test_scrolling_keeps_the_related_notification_of_every_loaded_row(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    demo = demo_start()

    sent = now()
    for number in range(1, 81):
        create_test_app_notification(
            title=f'Notice {number:02d}', sent_datetime=sent - datetime.timedelta(minutes=number)
        )

    demo.goto('django_spire:notification:app:page:list')
    page.locator(SEARCH_INPUT).wait_for()

    titles = page.evaluate(LOAD_EVERY_PAGE, SEARCH_INPUT)

    assert titles == [f'Notice {number:02d}' for number in range(1, 81)]


def test_a_page_load_in_flight_does_not_overwrite_a_searched_reset(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    demo = demo_start()

    sent = now()
    for number in range(1, 81):
        create_test_app_notification(
            title=f'Notice {number:02d}', sent_datetime=sent - datetime.timedelta(minutes=number)
        )

    demo.goto('django_spire:notification:app:page:list')
    page.locator(SEARCH_INPUT).wait_for()
    page.wait_for_function(
        '(searchInput) => Alpine.$data(document.querySelector(searchInput)'
        '.closest("[x-data]")).items.length > 0',
        arg=SEARCH_INPUT,
    )

    titles = page.evaluate(LOAD_MORE_DURING_SEARCH, SEARCH_INPUT)

    assert sorted(titles) == [f'Notice {number}' for number in range(70, 80)]
