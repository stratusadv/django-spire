from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from test_project.apps.infinite_scrolling.tests.test_playwright.pages import (
    InfiniteScrollingCardPage,
    InfiniteScrollingDetailPage,
    InfiniteScrollingListPage,
    InfiniteScrollingTablePage,
)

if TYPE_CHECKING:
    from playwright.sync_api import Page
    from pytest_django.plugin import _LiveServer

    from test_project.apps.infinite_scrolling.models import InfiniteScrolling


pytest_plugins = ['django_spire.testing.playwright.fixtures']


@pytest.fixture
def card_page(authenticated_page: Page, live_server: _LiveServer) -> InfiniteScrollingCardPage:
    return InfiniteScrollingCardPage(authenticated_page, live_server.url)


@pytest.fixture
def detail_page(authenticated_page: Page, live_server: _LiveServer, infinite_scrolling_data: list[InfiniteScrolling]) -> InfiniteScrollingDetailPage:
    return InfiniteScrollingDetailPage(authenticated_page, live_server.url, infinite_scrolling_data[0].pk)


@pytest.fixture
def infinite_scrolling_data(_transactional_db: None) -> list[InfiniteScrolling]:
    from test_project.apps.infinite_scrolling.models import InfiniteScrolling

    return [
        InfiniteScrolling.objects.create(
            name=f'Test Item {i}',
            description=f'Description for item {i}'
        )
        for i in range(30)
    ]


@pytest.fixture
def list_page(authenticated_page: Page, live_server: _LiveServer) -> InfiniteScrollingListPage:
    return InfiniteScrollingListPage(authenticated_page, live_server.url)


@pytest.fixture
def table_page(authenticated_page: Page, live_server: _LiveServer) -> InfiniteScrollingTablePage:
    return InfiniteScrollingTablePage(authenticated_page, live_server.url)
