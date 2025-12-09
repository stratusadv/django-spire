from __future__ import annotations

from django.test import TestCase

from django_spire import urls


class TestUrls(TestCase):
    def test_app_name_is_django_spire(self) -> None:
        assert urls.app_name == 'django_spire'

    def test_urlpatterns_is_list(self) -> None:
        assert isinstance(urls.urlpatterns, list)

    def test_urlpatterns_is_not_empty(self) -> None:
        assert len(urls.urlpatterns) > 0
