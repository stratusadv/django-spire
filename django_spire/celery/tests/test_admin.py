from __future__ import annotations

import pickle
from typing import TYPE_CHECKING

from celery import states
from django.test import SimpleTestCase
from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.celery.admin import CeleryTaskAdmin
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

    def test_changelist_view_links_to_change_view(self) -> None:
        task = self._create_task_with_result()

        response = self.client.get(reverse('admin:django_spire_celery_celerytask_changelist'))

        assert response.status_code == 200
        assert task.display_name in response.content.decode()
        assert f'celerytask/{task.pk}/change/' in response.content.decode()


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
