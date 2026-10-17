from __future__ import annotations

import pickle
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

from celery import states
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import SimpleTestCase
from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.celery.admin import CeleryTaskAdmin
from django_spire.celery.models import CeleryTask
from django_spire.celery.tests.factories import create_test_celery_task

if TYPE_CHECKING:
    from django.http import HttpResponse

RESULT_STRING = 'alpha-bravo-result'
TRACEBACK_STRING = 'Traceback (most recent call last): ZeroDivisionError: division by zero'


class CeleryTaskAdminTestCase(BaseTestCase):
    def _create_task_with_result(self) -> CeleryTask:
        return create_test_celery_task(state=states.SUCCESS, _result=pickle.dumps(RESULT_STRING))

    def test_change_view_displays_result_verbose(self) -> None:
        task = self._create_task_with_result()
        url = reverse('admin:django_spire_celery_celerytask_change', args=[task.pk])

        response = self.client.get(url)

        assert response.status_code == 200
        assert RESULT_STRING in response.content.decode()

    def test_changelist_view_links_to_change_view(self) -> None:
        task = self._create_task_with_result()

        response = self.client.get(reverse('admin:django_spire_celery_celerytask_changelist'))

        assert response.status_code == 200
        assert task.display_name in response.content.decode()
        assert f'celerytask/{task.pk}/change/' in response.content.decode()

    def test_change_view_displays_exception_traceback(self) -> None:
        task = create_test_celery_task(state=states.FAILURE, exception_traceback=TRACEBACK_STRING)
        url = reverse('admin:django_spire_celery_celerytask_change', args=[task.pk])

        response = self.client.get(url)

        assert response.status_code == 200
        assert TRACEBACK_STRING in response.content.decode()


CUSTOM_STATE = 'MAKING NOISES'


class CeleryTaskAdminCustomStateTestCase(BaseTestCase):
    def test_changelist_displays_custom_state(self) -> None:
        create_test_celery_task(state=CUSTOM_STATE)

        response = self.client.get(reverse('admin:django_spire_celery_celerytask_changelist'))

        assert 'Making Noises' in response.content.decode()

    def test_change_view_displays_custom_state(self) -> None:
        task = create_test_celery_task(state=CUSTOM_STATE)

        response = self.client.get(
            reverse('admin:django_spire_celery_celerytask_change', args=[task.pk])
        )

        assert 'Making Noises' in response.content.decode()

    def test_state_filter_includes_custom_state(self) -> None:
        create_test_celery_task(state=CUSTOM_STATE)

        response = self.client.get(reverse('admin:django_spire_celery_celerytask_changelist'))

        assert 'state=MAKING+NOISES' in response.content.decode()

    def test_state_filter_narrows_queryset(self) -> None:
        noise_task = create_test_celery_task(display_name='Noise Task', state=CUSTOM_STATE)
        quiet_task = create_test_celery_task(display_name='Quiet Task', state=states.SUCCESS)

        response = self.client.get(
            reverse('admin:django_spire_celery_celerytask_changelist'), {'state': CUSTOM_STATE}
        )

        content = response.content.decode()
        assert f'celerytask/{noise_task.pk}/change/' in content
        assert f'celerytask/{quiet_task.pk}/change/' not in content


class CeleryTaskAdminExceptionResultTestCase(SimpleTestCase):
    def test_exception_result_is_readonly_and_listed(self) -> None:
        assert 'exception_result' in CeleryTaskAdmin.readonly_fields
        assert 'exception_result' in CeleryTaskAdmin.fields

    def test_exception_traceback_is_readonly_and_listed(self) -> None:
        assert 'exception_traceback' in CeleryTaskAdmin.readonly_fields
        assert 'exception_traceback' in CeleryTaskAdmin.fields


class CeleryTaskAdminCancelActionTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.changelist_url = reverse('admin:django_spire_celery_celerytask_changelist')

    def _run_cancel_action(self, tasks: list[CeleryTask]) -> HttpResponse:
        post_data = {
            'action': 'cancel_selected_celery_tasks',
            'index': '0',
            '_selected_action': [str(task.pk) for task in tasks],
        }

        return self.client.post(self.changelist_url, post_data, follow=True)

    @patch('django_spire.celery.services.service.current_app')
    def test_action_cancels_queued_and_started_tasks(self, mock_app: MagicMock) -> None:
        queued = create_test_celery_task(state=states.PENDING)
        started = create_test_celery_task(state=states.STARTED)

        self._run_cancel_action([queued, started])

        queued.refresh_from_db()
        started.refresh_from_db()
        assert queued.state == states.REVOKED
        assert started.state == states.REVOKED
        assert mock_app.control.revoke.call_count == 2

    @patch('django_spire.celery.services.service.current_app')
    def test_action_skips_terminal_tasks_with_warning(self, mock_app: MagicMock) -> None:
        done = create_test_celery_task(state=states.SUCCESS)

        response = self._run_cancel_action([done])

        done.refresh_from_db()
        assert done.state == states.SUCCESS
        mock_app.control.revoke.assert_called_once()
        assert any('already finished' in str(message) for message in response.context['messages'])

    def test_action_is_not_permitted_without_change_permission(self) -> None:
        started = create_test_celery_task(state=states.STARTED)
        viewer = User.objects.create_user(username='viewer', is_staff=True)
        viewer.user_permissions.add(
            Permission.objects.get(
                content_type=ContentType.objects.get_for_model(CeleryTask),
                codename='view_celerytask',
            )
        )
        self.client.force_login(viewer)

        self._run_cancel_action([started])

        started.refresh_from_db()
        assert started.state == states.STARTED
