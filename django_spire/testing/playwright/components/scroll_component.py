from __future__ import annotations

from typing import TYPE_CHECKING, Any

from playwright.sync_api import expect

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


FIRST_SCROLL = """
    [...document.querySelectorAll('[x-data]')]
        .map(element => Alpine.$data(element))
        .find(data => data && 'loadGeneration' in data && 'rendersRows' in data)
"""


class ScrollComponent:
    """
    Playwright component for django_spire/component/scroll/base.html, the
    scroll a BaseScrollComponent renders.

    Row markup belongs to the consumer, so pass the selector matching one row
    of the page under test. The first scroll on the page is used unless
    root_selector names the element that carries a particular scroll's x-data:

        scroll = ScrollComponent(page, row_selector='tbody tr[data-scroll-key]')
        scroll.scroll_until_row_count(60)
        assert scroll.state()['hasMore'] is False
    """

    def __init__(
        self,
        page: Page,
        row_selector: str,
        root_selector: str | None = None,
    ) -> None:
        self.page = page
        self.row_selector = row_selector
        self.root_selector = root_selector

    @property
    def data_expression(self) -> str:
        if self.root_selector is None:
            return f'({FIRST_SCROLL})'

        return f"Alpine.$data(document.querySelector('{self.root_selector}'))"

    @property
    def rows(self) -> Locator:
        if self.root_selector is None:
            return self.page.locator(self.row_selector)

        return self.page.locator(self.root_selector).locator(self.row_selector)

    @property
    def state_expression(self) -> str:
        """
        JavaScript for the scroll's state, to embed in an evaluate that must
        read it in the same turn as something else.
        """
        return f"""
            (scroll => ({{
                hasMore: scroll.hasMore,
                isLoading: scroll.isLoading,
                items: [...scroll.items],
                loadedCount: scroll.loadedCount,
            }}))({self.data_expression})
        """.strip()

    def reload_items(self) -> dict[str, Any]:
        """Reload the list and return its state before it loads any further batch."""
        return self.page.evaluate(f"""
            async () => {{
                await {self.data_expression}.reloadItems()

                return {self.state_expression}
            }}
        """)

    def row_count(self) -> int:
        return self.rows.count()

    def scroll_to_bottom(self) -> None:
        self.page.mouse.wheel(0, 100_000)

    def scroll_until_row_count(self, count: int) -> None:
        self.rows.first.wait_for()
        shown = self.row_count()

        while shown < count:
            self.scroll_to_bottom()
            self.wait_for_row_count_above(shown)
            shown = self.row_count()

        self.wait_until_idle()

    def state(self) -> dict[str, Any]:
        return self.page.evaluate(f'() => {self.state_expression}')

    def wait_for_row_count(self, count: int) -> None:
        expect(self.rows).to_have_count(count)

    def wait_for_row_count_above(self, count: int) -> None:
        self.rows.nth(count).wait_for(state='attached')

    def wait_until_idle(self) -> None:
        self.page.wait_for_function(f'() => !{self.data_expression}.isLoading')
