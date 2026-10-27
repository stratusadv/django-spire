from __future__ import annotations

import re

from typing import TYPE_CHECKING

import pytest

from django.urls import reverse
from playwright.sync_api import expect

from django_spire.auth.user.tests.factories import create_user

if TYPE_CHECKING:
    from django.core.mail import EmailMessage
    from playwright.sync_api import Page
    from pytest_django.plugin import _LiveServer


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

OLD_PASSWORD = 'testpassword123'  # noqa: S105
NEW_PASSWORD = 'new-password-456'  # noqa: S105


def test_a_reset_link_sets_a_new_password_once(
    page: Page,
    live_server: _LiveServer,
    mailoutbox: list[EmailMessage],
    transactional_db: None,
) -> None:
    del transactional_db

    user = create_user(username='testuser', email='test@example.com')
    user.set_password(OLD_PASSWORD)
    user.save()

    login_url = f'{live_server.url}{reverse("django_spire:auth:admin:login")}'

    page.goto(f'{live_server.url}{reverse("django_spire:auth:admin:password_reset")}')
    page.fill('input[name="email"]', 'test@example.com')
    page.click('button[type="submit"]')
    expect(page).to_have_url(f'{live_server.url}{reverse("django_spire:auth:admin:password_reset_done")}')

    [email] = mailoutbox
    match = re.search(r'https?://\S+/password/reset/confirmation/[\w-]+/[\w-]+/', email.body)
    assert match is not None
    path = re.sub(r'^https?://[^/]+', '', match.group(0))

    page.goto(f'{live_server.url}{path}')
    page.fill('input[name="new_password1"]', NEW_PASSWORD)
    page.fill('input[name="new_password2"]', NEW_PASSWORD)
    page.click('button[type="submit"]')
    expect(page).to_have_url(f'{live_server.url}{reverse("django_spire:auth:admin:password_reset_complete")}')

    page.goto(login_url)
    page.fill('input[name="username"]', 'testuser')
    page.fill('input[name="password"]', NEW_PASSWORD)
    page.click('button[type="submit"]')
    expect(page).not_to_have_url(login_url)

    user.refresh_from_db()
    assert user.check_password(NEW_PASSWORD)
    assert not user.check_password(OLD_PASSWORD)

    page.goto(f'{live_server.url}{path}')
    expect(page.get_by_text('This password reset link is no longer valid')).to_be_visible()
    expect(page.locator('input[name="new_password1"]')).to_have_count(0)
