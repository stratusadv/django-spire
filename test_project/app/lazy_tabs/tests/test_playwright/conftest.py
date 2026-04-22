from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from test_project.apps.lazy_tabs.tests.test_playwright.pages import LazyTabsDemoPage

if TYPE_CHECKING:
    from playwright.sync_api import Page
    from pytest_django.plugin import _LiveServer


@pytest.fixture
def demo_page(authenticated_page: Page, live_server: _LiveServer) -> LazyTabsDemoPage:
    return LazyTabsDemoPage(authenticated_page, live_server.url)
