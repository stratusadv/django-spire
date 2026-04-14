from __future__ import annotations

from django.test import TestCase
from django.urls import reverse, resolve

from django_spire.celery.tests.factories import create_celery_task


class CeleryUrlsTestCase(TestCase):
    def test_celery_task_url_resolves(self) -> None:
        task = create_celery_task()
        url = reverse('django_spire:celery:task:toast', kwargs={'task_id': task.task_id})

        assert url == f'/django_spire/celery/task/{task.task_id}/'

    def test_celery_task_view_resolves(self) -> None:
        task = create_celery_task()
        resolved = resolve(f'/django_spire/celery/task/{task.task_id}/')

        assert resolved.view_name == 'django_spire:celery:task:toast'

    def test_celery_task_list_url_resolves(self) -> None:
        reference_key = 'test_reference_key'
        url = reverse(
            'django_spire:celery:task:toast_list', kwargs={'reference_key': reference_key}
        )

        assert url == f'/django_spire/celery/task/list/{reference_key}/'

    def test_celery_task_list_view_resolves(self) -> None:
        reference_key = 'test_reference_key'
        resolved = resolve(f'/django_spire/celery/task/list/{reference_key}/')

        assert resolved.view_name == 'django_spire:celery:task:toast_list'

    def test_celery_task_url_with_uuid(self) -> None:
        task = create_celery_task()
        url = reverse('django_spire:celery:task:toast', kwargs={'task_id': task.task_id})

        assert len(task.task_id) == 36

    def test_celery_task_list_url_with_different_reference_keys(self) -> None:
        key1 = 'reference_key_1'
        key2 = 'reference_key_2'

        url1 = reverse('django_spire:celery:task:toast_list', kwargs={'reference_key': key1})
        url2 = reverse('django_spire:celery:task:toast_list', kwargs={'reference_key': key2})

        assert url1 != url2
        assert key1 in url1
        assert key2 in url2
