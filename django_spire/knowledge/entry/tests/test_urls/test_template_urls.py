from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection


class EntryTemplateUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.collection = create_test_collection()

    def test_file_list_view_url_path(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:entry:template:file_list',
                kwargs={'collection_pk': self.collection.pk}
            )
        )
        assert response.status_code == 200

    def test_file_list_view_contains_files_json(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:entry:template:file_list',
                kwargs={'collection_pk': self.collection.pk}
            )
        )
        assert 'files_json' in response.context

    def test_file_list_view_contains_breadcrumbs(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:entry:template:file_list',
                kwargs={'collection_pk': self.collection.pk}
            )
        )
        assert 'breadcrumbs' in response.context
