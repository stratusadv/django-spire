from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.knowledge.entry.version.tests.factories import \
    create_test_entry_version


class EntryVersionJsonUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_entry = create_test_entry()
        self.test_entry_version = create_test_entry_version(entry=self.test_entry)
        self.test_entry.current_version = self.test_entry_version
        self.test_entry.save()

    def test_create_blank_block_view_url_path(self):
        response = self.client.post(
            reverse(
                'django_spire:knowledge:entry:version:json:create_blank_block',
                kwargs={'pk': self.test_entry_version.pk}
            ),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_block_view_url_path(self):
        response = self.client.post(
            reverse(
                'django_spire:knowledge:entry:version:json:delete_block',
                kwargs={'pk': self.test_entry_version.pk}
            ),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    def test_reorder_view_url_path(self):
        response = self.client.post(
            reverse(
                'django_spire:knowledge:entry:version:json:reorder',
                kwargs={'pk': self.test_entry_version.pk}
            ),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
