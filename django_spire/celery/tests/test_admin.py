from __future__ import annotations

from django.test import TestCase
from django.urls import reverse

from django_spire.celery.admin import CeleryTaskAdmin
from django_spire.celery.models import CeleryTask
from django_spire.celery.tests.factories import create_celery_task


class CeleryTaskAdminTestCase(TestCase):
    def setUp(self) -> None:
        self.celery_task = create_celery_task()

    def test_admin_changelist_view(self) -> None:
        response = self.client.get(
            reverse('django_spire_celery:django_spire_celery_celerytask_changelist')
        )

        assert response.status_code == 200
        assert self.celery_task in response.context['cl'].result_list

    def test_admin_changelist_displays_correct_columns(self) -> None:
        response = self.client.get(
            reverse('django_spire_celery:django_spire_celery_celerytask_changelist')
        )

        assert response.status_code == 200
        content = response.content.decode()
        assert self.celery_task.app_name in content
        assert self.celery_task.reference_name in content
        assert self.celery_task.state in content

    def test_admin_changelist_filters(self) -> None:
        response = self.client.get(
            reverse('django_spire_celery:django_spire_celery_celerytask_changelist')
        )

        assert response.status_code == 200
        assert 'filter' in response.content.decode().lower()

    def test_admin_changelist_search(self) -> None:
        response = self.client.get(
            reverse('django_spire_celery:django_spire_celery_celerytask_changelist'),
            data={'q': self.celery_task.app_name},
        )

        assert response.status_code == 200

    def test_admin_changelist_ordering(self) -> None:
        create_celery_task(reference_name='older_task')

        response = self.client.get(
            reverse('django_spire_celery:django_spire_celery_celerytask_changelist')
        )

        assert response.status_code == 200

    def test_admin_readonly_fields(self) -> None:
        admin = CeleryTaskAdmin(CeleryTask, None)

        expected_fields = [
            'task_id',
            'reference_key',
            'app_name',
            'reference_name',
            'state',
            'started_datetime',
            'estimated_completion_datetime',
            'completed_datetime',
        ]

        assert admin.readonly_fields == expected_fields

    def test_admin_fields(self) -> None:
        admin = CeleryTaskAdmin(CeleryTask, None)

        expected_fields = [
            'task_id',
            'reference_key',
            'app_name',
            'reference_name',
            'state',
            'started_datetime',
            'estimated_completion_datetime',
            'completed_datetime',
        ]

        assert admin.fields == expected_fields

    def test_admin_list_display(self) -> None:
        admin = CeleryTaskAdmin(CeleryTask, None)

        expected_display = (
            'app_name',
            'reference_name',
            'state',
            'started_datetime',
            'estimated_completion_datetime',
            'completed_datetime',
        )

        assert admin.list_display == expected_display

    def test_admin_list_filter(self) -> None:
        admin = CeleryTaskAdmin(CeleryTask, None)

        expected_filter = (
            'app_name',
            'reference_name',
            'state',
            'started_datetime',
            'completed_datetime',
        )

        assert admin.list_filter == expected_filter

    def test_admin_search_fields(self) -> None:
        admin = CeleryTaskAdmin(CeleryTask, None)

        expected_search = (
            'app_name',
            'reference_name',
            'state',
            'started_datetime',
            'completed_datetime',
        )

        assert admin.search_fields == expected_search

    def test_admin_ordering(self) -> None:
        admin = CeleryTaskAdmin(CeleryTask, None)

        assert admin.ordering == ('-started_datetime',)
