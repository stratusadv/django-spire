from __future__ import annotations

import os
import re
import pytest

from typing import Any, Callable, TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.urls import reverse

from limelight import Demo
from limelight.django import DjangoApplication

if TYPE_CHECKING:
    from playwright.sync_api import Page
    from pytest_django.plugin import _LiveServer


def pytest_configure(config: Any) -> None:
    del config
    os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'


@pytest.fixture
def authenticated_page(page: Page, live_server: _LiveServer, transactional_db: None) -> Page:
    del transactional_db

    password = b'testpass123'.decode()
    get_user_model().objects.create_user(
        username='testuser', password=password, is_staff=True, is_superuser=True
    )

    login_url = reverse('admin:login')
    index_url = reverse('admin:index')

    page.goto(f'{live_server.url}{login_url}')
    page.fill('input[name="username"]', 'testuser')
    page.fill('input[name="password"]', password)
    page.click('input[type="submit"]')
    page.wait_for_url(f'{live_server.url}{index_url}')

    return page


@pytest.fixture
def e2e_user(transactional_db: None) -> Any:
    """The superuser a limelight demo signs in as. Override downstream to change role."""
    del transactional_db

    return get_user_model().objects.create_superuser(username='limelight')


@pytest.fixture
def limelight_application(live_server: _LiveServer) -> DjangoApplication:
    """Limelight's handle on the running app; pair with ``demo_start``."""
    return DjangoApplication(live_server=live_server)


@pytest.fixture
def demo_start(
    page: Page,
    limelight_application: DjangoApplication,
    e2e_user: Any,
    request: pytest.FixtureRequest,
) -> Callable[..., Demo]:
    """
    Factory for a limelight ``Demo``. Its transcript and screenshots land under
    ``.demos/<test name>/`` (silent runs write nothing).

        def test_something(demo_start):
            demo = demo_start()
            demo.goto('app:page:list')
    """

    def start(**kwargs: Any) -> Demo:
        kwargs.setdefault('name', re.sub(r'[^\w.-]+', '_', request.node.name))
        kwargs.setdefault('user', e2e_user)

        return Demo(page, limelight_application, **kwargs)

    return start
