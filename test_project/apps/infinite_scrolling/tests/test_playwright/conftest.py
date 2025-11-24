from __future__ import annotations

import os
import pytest

from typing import Any, TYPE_CHECKING

from django.contrib.auth import get_user_model

from test_project.apps.infinite_scrolling.tests.test_playwright.pages.card_page import InfiniteScrollingCardPage
from test_project.apps.infinite_scrolling.tests.test_playwright.pages.detail_page import InfiniteScrollingDetailPage
from test_project.apps.infinite_scrolling.tests.test_playwright.pages.list_page import InfiniteScrollingListPage
from test_project.apps.infinite_scrolling.tests.test_playwright.pages.table_page import InfiniteScrollingTablePage

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from playwright.sync_api import Page
    from pytest_django.plugin import _LiveServer

    from test_project.apps.infinite_scrolling.models import InfiniteScrolling


User = get_user_model()


def pytest_configure(config: Any) -> None:
    os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any], playwright: Any) -> dict[str, Any]:
    return {
        **browser_context_args,
        "viewport": None,
        "no_viewport": True,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict[str, Any]) -> dict[str, Any]:
    return {
        **browser_type_launch_args,
        "args": ["--start-maximized"],
    }


@pytest.fixture
def authenticated_page(page: Page, live_server: _LiveServer, transactional_db: None) -> Page:
    User.objects.create_user(
        username='testuser',
        password='testpass123',
        is_staff=True,
        is_superuser=True
    )

    page.goto(f'{live_server.url}/admin/login/')
    page.fill('input[name="username"]', 'testuser')
    page.fill('input[name="password"]', 'testpass123')
    page.click('input[type="submit"]')
    page.wait_for_url(f'{live_server.url}/admin/')

    return page


@pytest.fixture
def infinite_scrolling_data(transactional_db: None) -> list[InfiniteScrolling]:
    from test_project.apps.infinite_scrolling.models import InfiniteScrolling

    items = []

    for i in range(30):
        items.append(
            InfiniteScrolling.objects.create(
                name=f'Test Item {i}',
                description=f'Description for item {i}'
            )
        )

    return items


@pytest.fixture
def list_page(authenticated_page: Page, live_server: _LiveServer) -> InfiniteScrollingListPage:
    return InfiniteScrollingListPage(authenticated_page, live_server.url)


@pytest.fixture
def table_page(authenticated_page: Page, live_server: _LiveServer) -> InfiniteScrollingTablePage:
    return InfiniteScrollingTablePage(authenticated_page, live_server.url)


@pytest.fixture
def card_page(authenticated_page: Page, live_server: _LiveServer) -> InfiniteScrollingCardPage:
    return InfiniteScrollingCardPage(authenticated_page, live_server.url)


@pytest.fixture
def detail_page(authenticated_page: Page, live_server: _LiveServer, infinite_scrolling_data: list[InfiniteScrolling]) -> InfiniteScrollingDetailPage:
    return InfiniteScrollingDetailPage(authenticated_page, live_server.url, infinite_scrolling_data[0].pk)
