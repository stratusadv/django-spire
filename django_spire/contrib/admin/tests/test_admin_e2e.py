from __future__ import annotations

import os
import pytest

from pathlib import Path
from typing_extensions import Any, TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse

from django_spire.contrib.admin.tests.factories import build_model_instances
from django_spire.contrib.admin.tests.test_admin_smoke import (
    changelist_url,
    registered_model_admins,
)

if TYPE_CHECKING:
    from playwright.sync_api import Page, Response
    from pytest_django.plugin import _LiveServer


pytestmark = [pytest.mark.e2e, pytest.mark.playwright]

DEMO_ROW_COUNT = 3
ERROR_TITLE_PREFIXES = ('Server Error', 'Page not found', 'Forbidden')
SCREENSHOT_ROOT = Path(os.getenv('ADMIN_DEMO_SCREENSHOT_DIR', 'test-results/admin_demo'))
TAKE_SCREENSHOTS = os.getenv('ADMIN_DEMO_SCREENSHOTS', '0') == '1'


@pytest.fixture
def seeded_admin_page(authenticated_page: Page, settings: Any, tmp_path: Path) -> Page:
    settings.MEDIA_ROOT = str(tmp_path / 'media')

    user = get_user_model().objects.get(username='testuser')
    generic_targets = [user, Group.objects.create(name='Demo Group')]

    for _, model_class, _ in registered_model_admins():
        build_model_instances(
            model_class,
            DEMO_ROW_COUNT,
            generic_targets=generic_targets,
        )

    return authenticated_page


def page_failure(page: Page, response: Response | None) -> str:
    if response is not None and response.status >= 400:
        return f'HTTP {response.status}'

    if page.title().startswith(ERROR_TITLE_PREFIXES):
        return page.title()

    return ''


def visit(page: Page, url: str, label: str) -> str:
    response = page.goto(url)
    page.wait_for_load_state('networkidle')

    if TAKE_SCREENSHOTS:
        SCREENSHOT_ROOT.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(SCREENSHOT_ROOT / f'{label}.png'), full_page=True)

    return page_failure(page, response)


class TestAdminWalkthrough:
    def test_walk_every_changelist(
        self,
        seeded_admin_page: Page,
        live_server: _LiveServer,
    ) -> None:
        failures = []

        for label, model_class, _ in registered_model_admins():
            url = f'{live_server.url}{changelist_url(model_class)}'
            failure = visit(seeded_admin_page, url, label)

            if failure:
                failures.append(f'{label} -> {failure}')

        assert not failures, f'admin changelists that failed in the browser: {failures}'

    def test_walk_every_change_form(
        self,
        seeded_admin_page: Page,
        live_server: _LiveServer,
    ) -> None:
        failures = []

        for label, model_class, _ in registered_model_admins():
            instance = model_class.objects.order_by('pk').first()

            if instance is None:
                continue

            meta = model_class._meta
            path = reverse(
                f'admin:{meta.app_label}_{meta.model_name}_change',
                args=[instance.pk],
            )

            failure = visit(seeded_admin_page, f'{live_server.url}{path}', f'{label}.change')

            if failure:
                failures.append(f'{label} -> {failure}')

        assert not failures, f'admin change forms that failed in the browser: {failures}'
