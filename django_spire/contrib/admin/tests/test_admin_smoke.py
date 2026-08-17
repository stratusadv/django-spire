from __future__ import annotations

import re

from html import unescape
from io import StringIO
from typing_extensions import TYPE_CHECKING

from django.contrib import admin
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from django_spire.contrib.admin.tests.factories import build_model_instances
from django_spire.core.tests.test_cases import BaseTestCase

if TYPE_CHECKING:
    from django.db.models import Model


BASELINE_ROW_COUNT = 2
SCALED_ROW_COUNT = 18
MAX_QUERY_GROWTH = SCALED_ROW_COUNT // 2

UNSEEDABLE_MODELS = frozenset({'django_spire_ai_context.organization'})

MAX_LINKS_PER_CHANGELIST = 24

QUERYSTRING_LINK_PATTERN = re.compile(r'href="(\?[^"]*)"')


def registered_model_admins() -> list[tuple[str, type, admin.ModelAdmin]]:
    entries = []

    for model_class, model_admin in admin.site._registry.items():
        meta = model_class._meta
        label = f'{meta.app_label}.{meta.model_name}'

        entry = (label, model_class, model_admin)
        entries.append(entry)

    return sorted(entries)


def changelist_url(model_class: type[Model]) -> str:
    meta = model_class._meta

    return reverse(f'admin:{meta.app_label}_{meta.model_name}_changelist')


class AdminSeedingMixin(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.generic_targets = [self.super_user, Group.objects.create(name='smoke group')]

    def seed_rows(self, model_class: type[Model], count: int, start_index: int = 0) -> int:
        instances = build_model_instances(
            model_class,
            count,
            start_index=start_index,
            generic_targets=self.generic_targets,
        )

        return len(instances)


class AdminSmokeTests(AdminSeedingMixin):
    def test_every_changelist_loads(self) -> None:
        failures = []

        for label, model_class, _ in registered_model_admins():
            self.seed_rows(model_class, BASELINE_ROW_COUNT)

            response = self.client.get(changelist_url(model_class))

            if response.status_code != 200:
                failures.append(f'{label} -> {response.status_code}')

        assert not failures, f'changelists that did not return 200: {failures}'

    def test_every_changelist_search_works(self) -> None:
        failures = []

        for label, model_class, model_admin in registered_model_admins():
            if not model_admin.search_fields:
                continue

            self.seed_rows(model_class, BASELINE_ROW_COUNT)

            response = self.client.get(changelist_url(model_class), {'q': 'seed'})

            if response.status_code != 200:
                failures.append(f'{label} -> {response.status_code}')

        assert not failures, f'admin searches that did not return 200: {failures}'

    def test_every_changelist_filter_and_sort_link_works(self) -> None:
        failures = []

        for label, model_class, _ in registered_model_admins():
            self.seed_rows(model_class, BASELINE_ROW_COUNT)

            url = changelist_url(model_class)
            response = self.client.get(url)

            if response.status_code != 200:
                failures.append(f'{label} -> changelist {response.status_code}')
                continue

            querystrings = QUERYSTRING_LINK_PATTERN.findall(response.content.decode())

            for querystring in sorted(set(querystrings))[:MAX_LINKS_PER_CHANGELIST]:
                link_response = self.client.get(url + unescape(querystring))

                if link_response.status_code != 200:
                    failures.append(f'{label} {querystring} -> {link_response.status_code}')

        assert not failures, f'admin filter/sort links that did not return 200: {failures}'

    def test_every_add_form_loads(self) -> None:
        failures = []

        for label, model_class, model_admin in registered_model_admins():
            request = self.client.get('/').wsgi_request

            if not model_admin.has_add_permission(request):
                continue

            meta = model_class._meta
            url = reverse(f'admin:{meta.app_label}_{meta.model_name}_add')

            response = self.client.get(url)

            if response.status_code != 200:
                failures.append(f'{label} -> {response.status_code}')

        assert not failures, f'add forms that did not return 200: {failures}'

    def test_every_change_form_loads(self) -> None:
        failures = []

        for label, model_class, _ in registered_model_admins():
            instances = build_model_instances(
                model_class,
                1,
                generic_targets=self.generic_targets,
            )

            if not instances:
                continue

            meta = model_class._meta
            url = reverse(
                f'admin:{meta.app_label}_{meta.model_name}_change',
                args=[instances[0].pk],
            )

            response = self.client.get(url)

            if response.status_code != 200:
                failures.append(f'{label} -> {response.status_code}')

        assert not failures, f'change forms that did not return 200: {failures}'


class AdminSeedCoverageTests(AdminSeedingMixin):
    def test_registered_models_are_seedable(self) -> None:
        unseedable = set()

        for label, model_class, _ in registered_model_admins():
            if self.seed_rows(model_class, BASELINE_ROW_COUNT) < BASELINE_ROW_COUNT:
                unseedable.add(label)

        unexpected = unseedable - UNSEEDABLE_MODELS

        assert not unexpected, (
            f'models the admin test factory can no longer build: {sorted(unexpected)}. '
            f'Every other admin test silently skips these, so fix the factory or add '
            f'them to UNSEEDABLE_MODELS.'
        )


class AdminSystemCheckTests(BaseTestCase):
    def test_admin_system_checks_pass(self) -> None:
        stderr = StringIO()

        call_command('check', '--fail-level', 'WARNING', stderr=stderr, stdout=StringIO())

        assert not stderr.getvalue(), stderr.getvalue()


class AdminQueryCountTests(AdminSeedingMixin):
    def changelist_query_count(self, model_class: type[Model]) -> int:
        url = changelist_url(model_class)

        self.client.get(url)

        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)

        assert response.status_code == 200, f'{model_class} -> {response.status_code}'

        return len(context.captured_queries)

    def test_changelist_query_count_does_not_scale_with_row_count(self) -> None:
        failures = []

        for label, model_class, _ in registered_model_admins():
            seeded = self.seed_rows(model_class, BASELINE_ROW_COUNT)

            if seeded < BASELINE_ROW_COUNT:
                continue

            baseline = self.changelist_query_count(model_class)

            scaled_seeded = self.seed_rows(
                model_class,
                SCALED_ROW_COUNT,
                start_index=BASELINE_ROW_COUNT,
            )

            if scaled_seeded < SCALED_ROW_COUNT:
                continue

            scaled = self.changelist_query_count(model_class)

            if scaled - baseline >= MAX_QUERY_GROWTH:
                failures.append(
                    f'{label}: {baseline} queries at {BASELINE_ROW_COUNT} rows -> '
                    f'{scaled} queries at {BASELINE_ROW_COUNT + SCALED_ROW_COUNT} rows'
                )

        assert not failures, (
            f'admin changelists whose query count grows with row count '
            f'(add select_related/prefetch_related to get_queryset): {failures}'
        )
