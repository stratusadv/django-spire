from __future__ import annotations

import uuid
from unittest.mock import MagicMock, patch

from celery import states
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from django_spire.api.choices import ApiPermissionChoices
from django_spire.api.models import ApiAccess
from django_spire.celery.models import CeleryTask
from django_spire.celery.tests.factories import create_test_celery_task
from django_spire.constants import BASE_URL_NAME
from django_spire.core.tests.test_cases import BaseTestCase

_CURRENT_APP = 'django_spire.celery.services.service.current_app'


class CeleryTaskApiTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.celery_task = create_test_celery_task(state=states.STARTED)

        self.change_key = self._create_key(
            'celery_change', 'change_celerytask', ApiPermissionChoices.CHANGE
        )
        self.view_key = self._create_key(
            'celery_view', 'change_celerytask', ApiPermissionChoices.VIEW
        )

    def _create_key(self, username: str, codename: str, api_permission: int) -> str:
        user = User.objects.create_user(username=username)
        content_type = ContentType.objects.get_for_model(CeleryTask)
        user.user_permissions.add(
            Permission.objects.get(content_type=content_type, codename=codename)
        )

        raw_key = f'{username}_key'
        api_access = ApiAccess.objects.create(name=username, permission=api_permission, user=user)
        api_access.set_key_and_save(raw_key)

        return raw_key

    def cancel_url(self, task_id: str | uuid.UUID | None = None) -> str:
        if task_id is None:
            task_id = self.celery_task.task_id

        return reverse(f'{BASE_URL_NAME}:api_v1:cancel_task', kwargs={'task_id': task_id})

    def post_cancel(self, raw_key: str | None):
        extra = {'HTTP_X_API_KEY': raw_key} if raw_key else {}

        return self.client.post(self.cancel_url(), **extra)


class CeleryTaskCancelApiTestCase(CeleryTaskApiTestCase):
    @patch(_CURRENT_APP)
    def test_change_key_cancels_task(self, mock_app: MagicMock) -> None:
        response = self.post_cancel(self.change_key)

        assert response.status_code == 200
        assert response.json()['state'] == states.REVOKED
        mock_app.control.revoke.assert_called_once_with(
            str(self.celery_task.task_id), terminate=True
        )

        self.celery_task.refresh_from_db()
        assert self.celery_task.state == states.REVOKED

    @patch(_CURRENT_APP)
    def test_second_cancel_returns_409(self, mock_app: MagicMock) -> None:
        assert self.post_cancel(self.change_key).status_code == 200

        response = self.post_cancel(self.change_key)

        assert response.status_code == 409
        assert 'error' in response.json()
        assert mock_app.control.revoke.call_count == 2

        self.celery_task.refresh_from_db()
        assert self.celery_task.state == states.REVOKED

    @patch(_CURRENT_APP)
    def test_insufficient_api_permission_is_rejected(self, mock_app: MagicMock) -> None:
        response = self.post_cancel(self.view_key)

        assert response.status_code == 401
        mock_app.control.revoke.assert_not_called()

        self.celery_task.refresh_from_db()
        assert self.celery_task.state == states.STARTED

    @patch(_CURRENT_APP)
    def test_missing_key_is_rejected(self, mock_app: MagicMock) -> None:
        response = self.post_cancel(None)

        assert response.status_code == 401
        mock_app.control.revoke.assert_not_called()

    @patch(_CURRENT_APP)
    def test_super_access_key_bypasses_permissions(self, mock_app: MagicMock) -> None:
        super_access = ApiAccess.objects.create(
            name='Super Key', permission=ApiPermissionChoices.VIEW, has_super_access=True
        )
        super_access.set_key_and_save('super_key')

        response = self.client.post(self.cancel_url(), HTTP_X_API_KEY='super_key')

        assert response.status_code == 200
        mock_app.control.revoke.assert_called_once()

        self.celery_task.refresh_from_db()
        assert self.celery_task.state == states.REVOKED

    def test_unknown_task_returns_404(self) -> None:
        response = self.client.post(self.cancel_url(uuid.uuid4()), HTTP_X_API_KEY=self.change_key)

        assert response.status_code == 404

    def test_malformed_task_id_returns_404(self) -> None:
        response = self.client.post(self.cancel_url('not-a-uuid'), HTTP_X_API_KEY=self.change_key)

        assert response.status_code == 404
