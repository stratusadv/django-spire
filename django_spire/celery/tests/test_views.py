from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from celery import states
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse

from django_spire.celery.models import CeleryTask
from django_spire.celery.tests.factories import create_test_celery_task
from django_spire.celery.views.task_views import (
    task_item_view,
    task_toast_view,
    task_item_list_view,
    task_toast_list_view,
)


class BaseTaskViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.celery_task = create_test_celery_task()
        self.super_user = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='test'
        )


class TaskItemViewTestCase(BaseTaskViewTestCase):
    def test_task_item_view_requires_login(self) -> None:
        self.client.logout()
        response = self.client.get(
            reverse('django_spire:celery:task:item', kwargs={'task_id': self.celery_task.task_id})
        )
        assert response.status_code == 302

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_item_view_retrieves_task(self, mock_get_object_or_404) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/item/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_item_view(request, str(self.celery_task.task_id))

        mock_get_object_or_404.assert_called_once_with(
            CeleryTask, task_id=str(self.celery_task.task_id)
        )
        assert response.status_code == 200

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_item_view_uses_correct_template(self, mock_get_object_or_404) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/item/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_item_view(request, str(self.celery_task.task_id))

        assert response.template_name == 'django_spire/celery/item/task_item.html'

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_item_view_passes_task_to_context(self, mock_get_object_or_404) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/item/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_item_view(request, str(self.celery_task.task_id))

        assert response.context_data['celery_task'] == self.celery_task

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    @patch.object(CeleryTask.services.__class__, 'update_from_async_result_and_save_if_change')
    def test_task_item_view_updates_task_from_async_result(
        self, mock_update, mock_get_object_or_404
    ) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/item/{self.celery_task.task_id}/')
        request.user = self.super_user

        task_item_view(request, str(self.celery_task.task_id))

        mock_update.assert_called_once()


class TaskToastViewTestCase(BaseTaskViewTestCase):
    def test_task_toast_view_requires_login(self) -> None:
        self.client.logout()
        response = self.client.get(
            reverse('django_spire:celery:task:toast', kwargs={'task_id': self.celery_task.task_id})
        )
        assert response.status_code == 302

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_toast_view_retrieves_task(self, mock_get_object_or_404) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/toast/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_toast_view(request, str(self.celery_task.task_id))

        mock_get_object_or_404.assert_called_once_with(
            CeleryTask, task_id=str(self.celery_task.task_id)
        )
        assert response.status_code == 200

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_toast_view_uses_correct_template(self, mock_get_object_or_404) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/toast/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_toast_view(request, str(self.celery_task.task_id))

        assert response.template_name == 'django_spire/celery/toast/task_toast.html'

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_toast_view_passes_task_to_context(self, mock_get_object_or_404) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/toast/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_toast_view(request, str(self.celery_task.task_id))

        assert response.context_data['celery_task'] == self.celery_task

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    @patch.object(CeleryTask.services.__class__, 'update_from_async_result_and_save_if_change')
    def test_task_toast_view_updates_task_from_async_result(
        self, mock_update, mock_get_object_or_404
    ) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/toast/{self.celery_task.task_id}/')
        request.user = self.super_user

        task_toast_view(request, str(self.celery_task.task_id))

        mock_update.assert_called_once()


class TaskItemListViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.super_user = User.objects.create_superuser(
            username='admin', email='admin@test.com', password='test'
        )
        self.reference_key = 'test_reference_key'
        self.task1 = create_test_celery_task(reference_key=self.reference_key, state=states.PENDING)
        self.task2 = create_test_celery_task(reference_key=self.reference_key, state=states.SUCCESS)
        self.task3 = create_test_celery_task(reference_key=self.reference_key, state=states.STARTED)

    def test_task_item_list_view_requires_login(self) -> None:
        self.client.logout()
        response = self.client.post(
            reverse('django_spire:celery:task:item_list'),
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        assert response.status_code == 302

    def test_task_item_list_view_retrieves_tasks(self) -> None:
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        assert response.status_code == 200

    def test_task_item_list_view_uses_correct_template(self) -> None:
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        assert response.template_name == 'django_spire/celery/item/task_item_list.html'

    def test_task_item_list_view_passes_tasks_to_context(self) -> None:
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        assert 'celery_tasks' in response.context_data

    def test_task_item_list_view_filters_unready_tasks(self) -> None:
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        tasks = list(response.context_data['celery_tasks'])
        assert self.task1 in tasks
        assert self.task2 not in tasks
        assert self.task3 in tasks

    def test_task_item_list_view_with_show_all_parameter(self) -> None:
        request = self.factory.post(
            f'/celery/task/item_list/?show_all=true',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user
        request.GET = {'show_all': 'true'}

        response = task_item_list_view(request)

        tasks = list(response.context_data['celery_tasks'])
        assert self.task1 in tasks
        assert self.task2 in tasks
        assert self.task3 in tasks

    def test_task_item_list_view_with_model_key(self) -> None:
        reference_with_model = f'{self.reference_key}|model_key_1'
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': reference_with_model}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        assert response.status_code == 200


class TaskToastListViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.super_user = User.objects.create_superuser(
            username='admin2', email='admin2@test.com', password='test'
        )
        self.reference_key = 'test_reference_key'
        self.task1 = create_test_celery_task(reference_key=self.reference_key, state=states.PENDING)
        self.task2 = create_test_celery_task(reference_key=self.reference_key, state=states.SUCCESS)
        self.task3 = create_test_celery_task(reference_key=self.reference_key, state=states.STARTED)

    def test_task_toast_list_view_requires_login(self) -> None:
        self.client.logout()
        response = self.client.post(
            reverse('django_spire:celery:task:toast_list'),
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        assert response.status_code == 302

    def test_task_toast_list_view_retrieves_tasks(self) -> None:
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_toast_list_view(request)

        assert response.status_code == 200

    def test_task_toast_list_view_uses_correct_template(self) -> None:
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_toast_list_view(request)

        assert response.template_name == 'django_spire/celery/toast/task_toast_list.html'

    def test_task_toast_list_view_passes_tasks_to_context(self) -> None:
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_toast_list_view(request)

        assert 'celery_tasks' in response.context_data

    def test_task_toast_list_view_filters_unready_tasks(self) -> None:
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_toast_list_view(request)

        tasks = list(response.context_data['celery_tasks'])
        assert self.task1 in tasks
        assert self.task2 not in tasks
        assert self.task3 in tasks

    def test_task_toast_list_view_with_show_all_parameter(self) -> None:
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json'
        )
        request.user = self.super_user
        request.GET = {'show_all': 'true'}

        response = task_toast_list_view(request)

        tasks = list(response.context_data['celery_tasks'])
        assert self.task1 in tasks
        assert self.task2 in tasks
        assert self.task3 in tasks

    def test_task_toast_list_view_with_multiple_keys(self) -> None:
        other_key = 'other_reference_key'
        create_test_celery_task(reference_key=other_key, state=states.PENDING)

        key_pairs = f'{self.reference_key},{other_key}'
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': key_pairs}),
            content_type='application/json'
        )
        request.user = self.super_user

        response = task_toast_list_view(request)

        assert response.status_code == 200