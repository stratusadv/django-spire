from __future__ import annotations

from unittest.mock import patch

from celery import states
from django.test import RequestFactory
from django.urls import reverse

from django_spire.celery.models import CeleryTask
from django_spire.celery.tests.factories import create_celery_task
from django_spire.celery.views.task_views import task_toast_list_view, task_toast_view
from django_spire.core.tests.test_cases import BaseTestCase


class TaskViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()
        self.celery_task = create_celery_task()

    def test_task_view_requires_login(self) -> None:
        self.client.logout()
        response = self.client.get(
            reverse('django_spire:celery:task:toast', kwargs={'task_id': self.celery_task.task_id})
        )
        assert response.status_code == 302

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_view_retrieves_task(self, mock_get_object_or_404) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/task/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_toast_view(request, self.celery_task.task_id)

        mock_get_object_or_404.assert_called_once_with(CeleryTask, task_id=self.celery_task.task_id)
        assert response.status_code == 200

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_view_uses_correct_template(self, mock_get_object_or_404) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/task/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_toast_view(request, self.celery_task.task_id)

        assert response.template_name == 'django_spire/celery/toast/task_toast.html'

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_view_passes_task_to_context(self, mock_get_object_or_404) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/task/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_toast_view(request, self.celery_task.task_id)

        assert response.context_data['celery_task'] == self.celery_task

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    @patch('django_spire.celery.models.CeleryTask.update_from_async_result_and_save')
    def test_task_view_updates_task_from_async_result(
        self, mock_update, mock_get_object_or_404
    ) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/task/{self.celery_task.task_id}/')
        request.user = self.super_user

        task_toast_view(request, self.celery_task.task_id)

        mock_update.assert_called_once()


class TaskListViewTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()
        self.reference_key = 'test_reference_key'
        self.task1 = create_celery_task(reference_key=self.reference_key, state=states.PENDING)
        self.task2 = create_celery_task(reference_key=self.reference_key, state=states.SUCCESS)
        self.task3 = create_celery_task(reference_key=self.reference_key, state=states.STARTED)

    def test_task_toast_list_view_requires_login(self) -> None:
        self.client.logout()
        response = self.client.get(
            reverse(
                'django_spire:celery:task:toast_list', kwargs={'reference_key': self.reference_key}
            )
        )
        assert response.status_code == 302

    def test_task_toast_list_view_retrieves_tasks(self) -> None:
        request = self.factory.get(f'/task/list/{self.reference_key}/')
        request.user = self.super_user

        response = task_toast_list_view(request, self.reference_key)

        assert response.status_code == 200

    def test_task_toast_list_view_uses_correct_template(self) -> None:
        request = self.factory.get(f'/task/list/{self.reference_key}/')
        request.user = self.super_user

        response = task_toast_list_view(request, self.reference_key)

        assert response.template_name == 'django_spire/celery/toast/task_toast_list.html'

    def test_task_toast_list_view_passes_tasks_to_context(self) -> None:
        request = self.factory.get(f'/task/list/{self.reference_key}/')
        request.user = self.super_user

        response = task_toast_list_view(request, self.reference_key)

        assert 'celery_tasks' in response.context_data

    def test_task_toast_list_view_filters_by_reference_key(self) -> None:
        other_key = 'other_reference_key'
        create_celery_task(reference_key=other_key, state=states.PENDING)

        request = self.factory.get(f'/task/list/{self.reference_key}/')
        request.user = self.super_user

        response = task_toast_list_view(request, self.reference_key)

        tasks = response.context_data['celery_tasks']
        assert self.task1 in tasks
        assert self.task2 not in tasks
        assert self.task3 in tasks

    def test_task_toast_list_view_filters_unready_only(self) -> None:
        request = self.factory.get(f'/task/list/{self.reference_key}/')
        request.user = self.super_user

        response = task_toast_list_view(request, self.reference_key)

        tasks = list(response.context_data['celery_tasks'])
        assert self.task1 in tasks
        assert self.task2 not in tasks
        assert self.task3 in tasks

    def test_task_toast_list_view_empty_when_no_matching_tasks(self) -> None:
        request = self.factory.get('/task/list/nonexistent_key/')
        request.user = self.super_user

        response = task_toast_list_view(request, 'nonexistent_key')

        assert response.status_code == 200
        assert list(response.context_data['celery_tasks']) == []
