from __future__ import annotations

import os
import pytest

from typing import Any, TYPE_CHECKING

from django.contrib.auth import get_user_model

from test_project.apps.lazy_tabs.tests.test_playwright.pages.demo_page import LazyTabsDemoPage

if TYPE_CHECKING:
    from playwright.sync_api import Page
    from pytest_django.plugin import _LiveServer


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
def demo_page(authenticated_page: Page, live_server: _LiveServer) -> LazyTabsDemoPage:
    return LazyTabsDemoPage(authenticated_page, live_server.url)
