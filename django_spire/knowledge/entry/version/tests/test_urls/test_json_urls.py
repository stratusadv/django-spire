from __future__ import annotations

import json

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.knowledge.entry.version.block.tests.factories import create_test_block_form_data
from django_spire.knowledge.entry.version.tests.factories import create_test_entry_version


class EntryVersionJsonUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()
        self.test_entry = create_test_entry(collection=self.collection)
        self.test_entry_version = create_test_entry_version(entry=self.test_entry)
        self.test_entry.current_version = self.test_entry_version
        self.test_entry.save()

    def test_update_blocks_view(self):
        response = self.client.post(
            reverse(
                'django_spire:knowledge:entry:version:json:update_blocks',
                kwargs={'pk': self.test_entry_version.pk}
            ),
            data=json.dumps([create_test_block_form_data()]),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_update_blocks_view_empty_list(self):
        response = self.client.post(
            reverse(
                'django_spire:knowledge:entry:version:json:update_blocks',
                kwargs={'pk': self.test_entry_version.pk}
            ),
            data=json.dumps([]),
            content_type='application/json'
        )
        assert response.status_code == 200

    def test_update_entry_from_version_view(self):
        response = self.client.post(
            reverse(
                'django_spire:knowledge:entry:version:json:update_entry_from_version',
                kwargs={'pk': self.test_entry_version.pk}
            ),
            content_type='application/json'
        )
        assert response.status_code == 200
