from __future__ import annotations

import os
import pytest

from typing import Any, TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.urls import reverse

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
