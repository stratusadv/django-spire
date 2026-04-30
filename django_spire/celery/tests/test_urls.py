from __future__ import annotations

import uuid

from django.test import TestCase
from django.urls import reverse, resolve


class CeleryTaskUrlsTestCase(TestCase):
    def test_task_item_url_resolves(self) -> None:
        task_id = str(uuid.uuid4())
        url = reverse('django_spire:celery:task:item', kwargs={'task_id': task_id})

        assert url == f'/django_spire/celery/task/item/{task_id}/'

        resolved = resolve(f'/django_spire/celery/task/item/{task_id}/')
        assert resolved.kwargs['task_id'] == task_id

    def test_task_toast_url_resolves(self) -> None:
        task_id = str(uuid.uuid4())
        url = reverse('django_spire:celery:task:toast', kwargs={'task_id': task_id})

        assert url == f'/django_spire/celery/task/toast/{task_id}/'

        resolved = resolve(f'/django_spire/celery/task/toast/{task_id}/')
        assert resolved.kwargs['task_id'] == task_id

    def test_task_item_list_url_resolves(self) -> None:
        url = reverse('django_spire:celery:task:item_list')

        assert url == '/django_spire/celery/task/item_list/'

        resolved = resolve('/django_spire/celery/task/item_list/')
        assert resolved.url_name == 'item_list'

    def test_task_toast_list_url_resolves(self) -> None:
        url = reverse('django_spire:celery:task:toast_list')

        assert url == '/django_spire/celery/task/toast_list/'

        resolved = resolve('/django_spire/celery/task/toast_list/')
        assert resolved.url_name == 'toast_list'

    def test_urls_have_different_paths(self) -> None:
        task_id = str(uuid.uuid4())

        item_url = reverse('django_spire:celery:task:item', kwargs={'task_id': task_id})
        toast_url = reverse('django_spire:celery:task:toast', kwargs={'task_id': task_id})
        item_list_url = reverse('django_spire:celery:task:item_list')
        toast_list_url = reverse('django_spire:celery:task:toast_list')

        assert item_url != toast_url
        assert item_url != item_list_url
        assert item_url != toast_list_url
        assert toast_url != item_list_url
        assert toast_url != toast_list_url
        assert item_list_url != toast_list_url