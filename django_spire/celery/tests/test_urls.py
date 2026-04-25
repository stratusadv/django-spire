from __future__ import annotations

from django.test import TestCase
from django.urls import reverse


class CeleryUrlsTestCase(TestCase):
    def test_celery_task_list_url_with_different_reference_keys(self) -> None:
        key1 = 'reference_key_1'
        key2 = 'reference_key_2'

        url1 = reverse('django_spire:celery:task:toast_list', kwargs={'reference_key': key1})
        url2 = reverse('django_spire:celery:task:toast_list', kwargs={'reference_key': key2})

        assert url1 != url2
        assert key1 in url1
        assert key2 in url2
