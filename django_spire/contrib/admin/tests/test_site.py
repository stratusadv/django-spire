from __future__ import annotations

import importlib.metadata

from django import __version__ as django_version
from django.contrib import admin
from django.urls import reverse

from django_spire import constants
from django_spire.core.tests.test_cases import BaseTestCase


class AdminSiteTitleTests(BaseTestCase):
    def test_site_title_shows_package_versions(self) -> None:
        glue_version = importlib.metadata.version('django-glue')
        expected = f'Django {django_version} Spire {constants.__VERSION__} Glue {glue_version} Admin Panel'

        assert admin.site.site_header == expected
        assert admin.site.site_title == expected

    def test_site_title_renders_in_admin_header(self) -> None:
        response = self.client.get(reverse('admin:index'))

        assert response.status_code == 200
        self.assertContains(response, admin.site.site_header)
