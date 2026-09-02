from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class GlueScroll:
    """
    Playwright component for django_spire/glue/scroll/scroll.html -- the v1
    glue-backed infinite scroll.

    Rows render client-side from a GlueQuerySetProxy, so assertions have to wait
    for a fetch to land rather than reading server-rendered HTML.

    The base template owns only the loading spinner and the empty state; row
    markup comes entirely from the consumer's scroll_template_item block. Pass
    the selector matching one row for the page under test:

        scroll = GlueScroll(page, row_selector='.row.border-bottom')
        scroll.wait_for_rows()
        scroll.search('prod')
        scroll.wait_for_row_count(1)
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
    def root(self) -> Locator:
        if self.root_selector is None:
            return self.page.locator('body')

        return self.page.locator(self.root_selector)

    @property
    def rows(self) -> Locator:
        return self.root.locator(self.row_selector)

    @property
    def spinner(self) -> Locator:
        """Owned by the base template -- shown while hasMore is true."""
        return self.root.locator('.spinner-border')

    def row_count(self) -> int:
        return self.rows.count()

    def row_texts(self) -> list[str]:
        rows = self.rows
        return [rows.nth(i).inner_text() for i in range(rows.count())]

    def is_loading(self) -> bool:
        return self.spinner.is_visible()

    def search(self, text: str) -> None:
        """Fill the scroll's search input -- every consumer's scroll_header
        block renders one `input[type="search"]` bound to `searchQuery`.
        """
        self.root.locator('input[type="search"]').fill(text)

    def scroll_to_bottom(self) -> None:
        """Trigger the IntersectionObserver sentinel that calls loadMoreItems()."""
        self.page.mouse.wheel(0, 100_000)

    def wait_for_rows(self, timeout: int = 10_000) -> None:
        self.rows.first.wait_for(timeout=timeout)

    def wait_for_row_count(self, count: int, timeout: int = 10_000) -> None:
        self.page.wait_for_function(
            '([selector, expected]) => document.querySelectorAll(selector).length === expected',
            arg=[self.row_selector, count],
            timeout=timeout,
        )

    def wait_for_row_count_to_increase(self, previous: int, timeout: int = 10_000) -> None:
        self.page.wait_for_function(
            '([selector, previous]) => document.querySelectorAll(selector).length > previous',
            arg=[self.row_selector, previous],
            timeout=timeout,
        )
