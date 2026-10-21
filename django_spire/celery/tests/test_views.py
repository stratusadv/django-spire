from __future__ import annotations

import json
import pickle
import uuid
from unittest.mock import MagicMock, patch

from celery import states
from django.contrib.auth.context_processors import PermWrapper
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase
from django.urls import reverse
from django.utils.timezone import now

from django_spire.celery.models import CeleryTask
from django_spire.celery.result import CeleryExceptionResult, CeleryNoResult
from django_spire.celery.tests.factories import create_test_celery_task
from django_spire.celery.views.task_views import (
    task_item_view,
    task_toast_view,
    task_item_list_view,
    task_toast_list_view,
)

_TRACK_CONFIGURED = (
    'django_spire.metric.domain.statistic.services.tracking_service'
    '.StatisticTrackingService.track_configured'
)


class BaseTaskViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.celery_task = create_test_celery_task()
        self.super_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='test',  # noqa: S106
        )


class TaskItemViewTestCase(BaseTaskViewTestCase):
    def test_task_item_view_requires_login(self) -> None:
        self.client.logout()
        response = self.client.get(
            reverse('django_spire:celery:task:item', kwargs={'task_id': self.celery_task.task_id})
        )
        assert response.status_code == 302

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_item_view_retrieves_task(self, mock_get_object_or_404: MagicMock) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/item/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_item_view(request, str(self.celery_task.task_id))

        mock_get_object_or_404.assert_called_once_with(
            CeleryTask, task_id=str(self.celery_task.task_id)
        )
        assert response.status_code == 200

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_item_view_uses_correct_template(self, mock_get_object_or_404: MagicMock) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/item/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_item_view(request, str(self.celery_task.task_id))

        assert response.template_name == 'django_spire/celery/item/task_item.html'

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_item_view_passes_task_to_context(self, mock_get_object_or_404: MagicMock) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/item/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_item_view(request, str(self.celery_task.task_id))

        assert response.context_data['celery_task'] == self.celery_task

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    @patch.object(CeleryTask.services.__class__, 'update_from_backend')
    def test_task_item_view_updates_task_from_backend(
        self, mock_update: MagicMock, mock_get_object_or_404: MagicMock
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
    def test_task_toast_view_retrieves_task(self, mock_get_object_or_404: MagicMock) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/toast/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_toast_view(request, str(self.celery_task.task_id))

        mock_get_object_or_404.assert_called_once_with(
            CeleryTask, task_id=str(self.celery_task.task_id)
        )
        assert response.status_code == 200

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_toast_view_uses_correct_template(self, mock_get_object_or_404: MagicMock) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/toast/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_toast_view(request, str(self.celery_task.task_id))

        assert response.template_name == 'django_spire/celery/toast/task_toast.html'

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    def test_task_toast_view_passes_task_to_context(
        self, mock_get_object_or_404: MagicMock
    ) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/toast/{self.celery_task.task_id}/')
        request.user = self.super_user

        response = task_toast_view(request, str(self.celery_task.task_id))

        assert response.context_data['celery_task'] == self.celery_task

    @patch('django_spire.celery.views.task_views.get_object_or_404')
    @patch.object(CeleryTask.services.__class__, 'update_from_backend')
    def test_task_toast_view_updates_task_from_backend(
        self, mock_update: MagicMock, mock_get_object_or_404: MagicMock
    ) -> None:
        mock_get_object_or_404.return_value = self.celery_task

        request = self.factory.get(f'/celery/task/toast/{self.celery_task.task_id}/')
        request.user = self.super_user

        task_toast_view(request, str(self.celery_task.task_id))

        mock_update.assert_called_once()
        mock_update.assert_called_once()


class TaskContentFailureDisplayTestCase(SimpleTestCase):
    def _failed_row(self, _result: bytes) -> CeleryTask:
        return CeleryTask(
            task_id=uuid.uuid4(),
            task_name='test_task',
            display_name='Test Task',
            reference_key='test_reference_key',
            state=states.FAILURE,
            _task_meta={},
            _result=_result,
        )

    def _render_content(self, celery_task: CeleryTask) -> str:
        return render_to_string(
            'django_spire/celery/content/task_content.html',
            {'celery_task': celery_task, 'task_header_class': '', 'task_body_class': ''},
        )

    def test_failure_block_shows_exception_message(self) -> None:
        celery_task = self._failed_row(
            pickle.dumps(CeleryExceptionResult(ValueError('boom'), None, 'traceback'))
        )

        html = self._render_content(celery_task)

        assert 'Task Encountered an Error: boom' in html

    def test_failure_block_falls_back_for_legacy_rows(self) -> None:
        celery_task = self._failed_row(pickle.dumps(CeleryNoResult()))

        html = self._render_content(celery_task)

        assert 'Task Encountered an Error or Took to Long' in html


class TaskItemListViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.super_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='test',  # noqa: S106
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
            content_type='application/json',
        )
        assert response.status_code == 302

    def test_task_item_list_view_retrieves_tasks(self) -> None:
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json',
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        assert response.status_code == 200

    def test_task_item_list_view_uses_correct_template(self) -> None:
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json',
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        assert response.template_name == 'django_spire/celery/item/task_item_list.html'

    def test_task_item_list_view_passes_tasks_to_context(self) -> None:
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json',
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        assert 'celery_tasks' in response.context_data

    def test_task_item_list_view_filters_unready_tasks(self) -> None:
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json',
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        tasks = list(response.context_data['celery_tasks'])
        assert self.task1 in tasks
        assert self.task2 not in tasks
        assert self.task3 in tasks

    @patch(_TRACK_CONFIGURED)
    def test_task_item_list_view_resolves_finished_tasks_from_backend(
        self, mock_track_configured: MagicMock
    ) -> None:
        pending_result = MagicMock()
        pending_result._get_task_meta.return_value = {'status': states.PENDING, 'result': None}
        pending_result.backend.get_task_meta.return_value = {
            'status': states.PENDING,
            'result': None,
        }

        finished_result = MagicMock()
        finished_result._get_task_meta.return_value = {'status': states.SUCCESS, 'result': None}
        finished_result.get.return_value = 'finished'
        finished_result.backend.get_task_meta.return_value = {
            'status': states.PENDING,
            'result': None,
        }

        def async_result_getter(celery_task: CeleryTask) -> MagicMock:
            if celery_task.pk == self.task1.pk:
                return pending_result
            return finished_result

        with patch.object(CeleryTask, 'async_result', new=property(async_result_getter)):
            request = self.factory.post(
                '/celery/task/item_list/',
                data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
                content_type='application/json',
            )
            request.user = self.super_user

            response = task_item_list_view(request)

        tasks = list(response.context_data['celery_tasks'])
        assert self.task1 in tasks
        assert self.task3 not in tasks

        self.task3.refresh_from_db()
        assert self.task3.state == states.SUCCESS
        assert self.task3.result == 'finished'
        mock_track_configured.assert_called_once_with(reference='celery_task_success')

    def test_task_item_list_view_with_show_all_parameter(self) -> None:
        request = self.factory.post(
            '/celery/task/item_list/',
            data=json.dumps(
                {'django_spire_celery_task_key_pairs': self.reference_key, 'show_all': True}
            ),
            content_type='application/json',
        )
        request.user = self.super_user

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
            content_type='application/json',
        )
        request.user = self.super_user

        response = task_item_list_view(request)

        assert response.status_code == 200


class TaskToastListViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.super_user = User.objects.create_superuser(
            username='admin2',
            email='admin2@test.com',
            password='test',  # noqa: S106
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
            content_type='application/json',
        )
        assert response.status_code == 302

    def test_task_toast_list_view_retrieves_tasks(self) -> None:
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json',
        )
        request.user = self.super_user

        response = task_toast_list_view(request)

        assert response.status_code == 200

    def test_task_toast_list_view_uses_correct_template(self) -> None:
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json',
        )
        request.user = self.super_user

        response = task_toast_list_view(request)

        assert response.template_name == 'django_spire/celery/toast/task_toast_list.html'

    def test_task_toast_list_view_passes_tasks_to_context(self) -> None:
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json',
        )
        request.user = self.super_user

        response = task_toast_list_view(request)

        assert 'celery_tasks' in response.context_data

    def test_task_toast_list_view_filters_unready_tasks(self) -> None:
        request = self.factory.post(
            '/celery/task/toast_list/',
            data=json.dumps({'django_spire_celery_task_key_pairs': self.reference_key}),
            content_type='application/json',
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
            data=json.dumps(
                {'django_spire_celery_task_key_pairs': self.reference_key, 'show_all': True}
            ),
            content_type='application/json',
        )
        request.user = self.super_user

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
            content_type='application/json',
        )
        request.user = self.super_user

        response = task_toast_list_view(request)

        assert response.status_code == 200


class TaskCancelViewTestCase(BaseTaskViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.cancel_url = reverse(
            'django_spire:celery:task:cancel', kwargs={'task_id': self.celery_task.task_id}
        )
        self.plain_user = User.objects.create_user(
            username='plain',
            email='plain@test.com',
            password='test',  # noqa: S106
        )

    @patch('django_spire.celery.services.service.current_app')
    def test_cancel_view_requires_login(self, mock_app: MagicMock) -> None:
        self.client.logout()
        response = self.client.post(self.cancel_url)

        assert response.status_code == 302
        mock_app.control.revoke.assert_not_called()

    @patch('django_spire.celery.services.service.current_app')
    def test_cancel_view_requires_change_permission(self, mock_app: MagicMock) -> None:
        self.client.force_login(self.plain_user)
        response = self.client.post(self.cancel_url)

        assert response.status_code == 403
        mock_app.control.revoke.assert_not_called()

    @patch('django_spire.celery.services.service.current_app')
    def test_cancel_view_rejects_get(self, mock_app: MagicMock) -> None:
        self.client.force_login(self.super_user)
        response = self.client.get(self.cancel_url)

        assert response.status_code == 405
        mock_app.control.revoke.assert_not_called()

    @patch('django_spire.celery.services.service.current_app')
    def test_cancel_view_cancels_task(self, mock_app: MagicMock) -> None:
        self.client.force_login(self.super_user)
        response = self.client.post(self.cancel_url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['canceled'] is True
        assert data['task_id'] == str(self.celery_task.task_id)
        mock_app.control.revoke.assert_called_once_with(
            str(self.celery_task.task_id), terminate=True
        )

        self.celery_task.refresh_from_db()
        assert self.celery_task.state == states.REVOKED
        assert self.celery_task.completed_datetime is not None

    @patch('django_spire.celery.services.service.current_app')
    def test_cancel_view_terminal_task_returns_error(self, mock_app: MagicMock) -> None:
        self.celery_task.state = states.SUCCESS
        self.celery_task.save()

        self.client.force_login(self.super_user)
        response = self.client.post(self.cancel_url)

        assert response.status_code == 409
        assert 'error' in json.loads(response.content)
        mock_app.control.revoke.assert_called_once_with(
            str(self.celery_task.task_id), terminate=True
        )

        self.celery_task.refresh_from_db()
        assert self.celery_task.state == states.SUCCESS

    def test_cancel_view_unknown_task_returns_404(self) -> None:
        self.client.force_login(self.super_user)
        url = reverse('django_spire:celery:task:cancel', kwargs={'task_id': uuid.uuid4()})
        response = self.client.post(url)

        assert response.status_code == 404


class TaskCancelContentTestCase(BaseTaskViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plain_user = User.objects.create_user(
            username='plain',
            email='plain@test.com',
            password='test',  # noqa: S106
        )

    def _render_content(self, user: User) -> str:
        return render_to_string(
            'django_spire/celery/item/task_item.html',
            context={
                'celery_task': self.celery_task,
                'task_header_class': 'ps-2 rounded-3',
                'task_body_class': 'px-2',
                'perms': PermWrapper(user),
            },
        )

    def test_cancel_button_renders_for_started_task_with_permission(self) -> None:
        self.celery_task.state = states.STARTED
        self.celery_task.save()

        html = self._render_content(self.super_user)

        assert 'aria-label="Cancel task"' in html
        assert 'Canceled at' not in html

    def test_cancel_button_renders_for_pending_task_with_permission(self) -> None:
        self.celery_task.state = states.PENDING
        self.celery_task.save()

        html = self._render_content(self.super_user)

        assert 'aria-label="Cancel task"' in html

    def test_cancel_button_hidden_without_permission(self) -> None:
        self.celery_task.state = states.STARTED
        self.celery_task.save()

        html = self._render_content(self.plain_user)

        assert 'aria-label="Cancel task"' not in html

    def test_cancel_button_hidden_for_canceled_task(self) -> None:
        self.celery_task.state = states.REVOKED
        self.celery_task.completed_datetime = now()
        self.celery_task.save()

        html = self._render_content(self.super_user)

        assert 'aria-label="Cancel task"' not in html
        assert 'Canceled at' in html
        assert 'bi-stop-circle-fill' in html

    def test_canceled_task_hides_button_even_with_permission(self) -> None:
        self.celery_task.state = states.SUCCESS
        self.celery_task.save()

        html = self._render_content(self.super_user)

        assert 'aria-label="Cancel task"' not in html
        assert 'Canceled at' not in html
