from __future__ import annotations

import pickle
from typing import TYPE_CHECKING

from celery import states
from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.celery.tests.factories import create_test_celery_task

if TYPE_CHECKING:
    from django_spire.celery.models import CeleryTask

RESULT_STRING = 'alpha-bravo-result'


class CeleryTaskAdminTestCase(BaseTestCase):
    def _create_task_with_result(self) -> CeleryTask:
        return create_test_celery_task(state=states.SUCCESS, _result=pickle.dumps(RESULT_STRING))

    def test_change_view_displays_result_verbose(self) -> None:
        task = self._create_task_with_result()
        url = reverse('admin:django_spire_celery_celerytask_change', args=[task.pk])

        response = self.client.get(url)

        assert response.status_code == 200
        assert RESULT_STRING in response.content.decode()

    def test_changelist_view_displays_result_verbose(self) -> None:
        self._create_task_with_result()

        response = self.client.get(reverse('admin:django_spire_celery_celerytask_changelist'))

        assert response.status_code == 200
        assert RESULT_STRING in response.content.decode()
