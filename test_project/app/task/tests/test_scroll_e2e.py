from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from playwright.sync_api import expect

from django_spire.testing.playwright.components.glue_scroll import GlueScroll

from test_project.app.task.models import Task
from test_project.app.task.tests.factories import create_test_task

if TYPE_CHECKING:
    from collections.abc import Callable

    from limelight import Demo
    from playwright.sync_api import Page


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]


def test_reset_and_load_busts_the_stale_scroll_query_cache(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    """
    scrollQuerySet is retained on the scroll component for its whole lifetime,
    and GlueQuerySetProxy caches a fetched page by its slice/filter/order
    params -- `all()` short-circuits to that cache once it has been loaded
    once. `updated-item` firing with `removed: true` calls resetAndLoad(),
    which reissues the *same* params, so before the fix it replayed straight
    from the stale cache and the removed row never left the DOM.

    Regression test for resetAndLoad() busting scrollQuerySet's cache
    (via .refresh()) before reloading.
    """
    del transactional_db

    keep = create_test_task(name='Keep Task')
    doomed = create_test_task(name='Doomed Task')

    demo = demo_start()
    demo.title('Scroll Reset Busts Its Stale Cache', kicker='django-spire')
    demo.goto('task:page:list')

    scroll = GlueScroll(page, row_selector='.row.border-bottom')
    scroll.wait_for_row_count(2)

    demo.narrate('scrollQuerySet has now cached this page of results', step='1')

    # Remove the row out from under the already-cached queryset, same as a
    # delete or a filter-changing edit would, then fire the event a consumer
    # dispatches on removal.
    doomed_pk = doomed.pk
    Task.objects.filter(pk=doomed_pk).update(is_deleted=True)

    page.evaluate(
        '(pk) => window.dispatchEvent('
        "new CustomEvent('updated-item', {detail: {pk, removed: true}})"
        ')',
        doomed_pk,
    )

    demo.narrate('The removed row disappears instead of replaying the stale cache', step='2')

    scroll.wait_for_row_count(1)
    expect(scroll.rows.first).to_contain_text(keep.name)
    expect(scroll.rows).not_to_contain_text('Doomed Task')


SCROLL_DATA = """
    () => [...document.querySelectorAll('[x-data]')]
        .map((element) => Alpine.$data(element))
        .find((data) => data && 'scrollQuerySet' in data)
"""

OVERLAPPING_RESETS = f"""
    async () => {{
        const scroll = ({SCROLL_DATA})()
        while (scroll.isLoading) await new Promise((resolve) => setTimeout(resolve, 50))

        const prototype = Object.getPrototypeOf(scroll.scrollQuerySet)
        const originalRefresh = prototype.refresh
        let refreshCount = 0
        let releaseSecond
        const secondGate = new Promise((resolve) => {{ releaseSecond = resolve }})

        prototype.refresh = async function () {{
            const call = ++refreshCount
            const result = await originalRefresh.call(this)
            if (call === 2) await secondGate
            return result
        }}

        try {{
            scroll.filterField = ''
            scroll.scrollQuerySet = scroll.scrollQuerySet.filter({{name__icontains: 'Needle'}})
            const first = scroll.resetAndLoad()
            const second = scroll.resetAndLoad()
            await first
            releaseSecond()
            await second
        }} finally {{
            prototype.refresh = originalRefresh
        }}

        return scroll.items.map((item) => item.name)
    }}
"""

LOAD_MORE_DURING_RESET = f"""
    async () => {{
        const scroll = ({SCROLL_DATA})()
        while (scroll.isLoading) await new Promise((resolve) => setTimeout(resolve, 50))
        if (!scroll.hasMore) throw new Error('the scroll must have another page to load')

        const prototype = Object.getPrototypeOf(scroll.scrollQuerySet)
        const originalLoadMore = prototype.loadMore
        let releaseLoadMore
        const loadMoreGate = new Promise((resolve) => {{ releaseLoadMore = resolve }})

        prototype.loadMore = async function (...args) {{
            await loadMoreGate
            return originalLoadMore.apply(this, args)
        }}

        try {{
            const loadMore = scroll.loadMoreItems()
            scroll.orderBy = '-name'
            await new Promise((resolve) => setTimeout(resolve, 1500))
            releaseLoadMore()
            await loadMore
            await new Promise((resolve) => setTimeout(resolve, 500))
        }} finally {{
            prototype.loadMore = originalLoadMore
        }}

        return scroll.items.map((item) => item.name)
    }}
"""


def test_an_overtaken_reset_does_not_replace_the_newer_reset_results(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    for number in range(1, 31):
        create_test_task(name=f'Task {number:02d}')

    create_test_task(name='Needle Task')

    demo = demo_start()
    demo.goto('task:page:list')

    scroll = GlueScroll(page, row_selector='.row.border-bottom')
    scroll.wait_for_rows()

    names = page.evaluate(OVERLAPPING_RESETS)

    assert names == ['Needle Task']
    scroll.wait_for_row_count(1)
    expect(scroll.rows.first).to_contain_text('Needle Task')


def test_a_page_load_in_flight_does_not_overwrite_a_reordered_reset(
    page: Page, demo_start: Callable[..., Demo], transactional_db: None
) -> None:
    del transactional_db

    for number in range(1, 81):
        create_test_task(name=f'Task {number:02d}')

    demo = demo_start()
    demo.goto('task:page:list')

    scroll = GlueScroll(page, row_selector='.row.border-bottom')
    scroll.wait_for_rows()

    names = page.evaluate(LOAD_MORE_DURING_RESET)

    assert names[0] == 'Task 80'
    assert names == sorted(names, reverse=True)
    assert len(names) == len(set(names))
