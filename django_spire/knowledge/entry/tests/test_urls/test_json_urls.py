from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.tests.factories import create_test_entry


class EntryJsonUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()
        self.test_entry = create_test_entry(collection=self.collection)

    def test_reorder_view_url_path(self):
        response = self.client.post(
            reverse('django_spire:knowledge:entry:json:reorder'),
            data={
                'entry_id': self.test_entry.pk,
                'order': 0,
                'collection_id': self.collection.pk
            },
            content_type='application/json',
        )
        assert response.status_code == 200

    def test_reorder_view_invalid_entry(self):
        response = self.client.post(
            reverse('django_spire:knowledge:entry:json:reorder'),
            data={
                'entry_id': 99999,
                'order': 0,
                'collection_id': self.collection.pk
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.json()['type'] == 'error'

    def test_reorder_view_missing_order(self):
        response = self.client.post(
            reverse('django_spire:knowledge:entry:json:reorder'),
            data={
                'entry_id': self.test_entry.pk,
                'collection_id': self.collection.pk
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.json()['type'] == 'error'

    def test_reorder_view_invalid_collection(self):
        response = self.client.post(
            reverse('django_spire:knowledge:entry:json:reorder'),
            data={
                'entry_id': self.test_entry.pk,
                'order': 0,
                'collection_id': 99999
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.json()['type'] == 'error'

    def test_update_files_view_url_path(self):
        response = self.client.post(
            reverse('django_spire:knowledge:entry:json:update_files'),
            content_type='application/json',
        )
        assert response.status_code == 200
        assert 'files_json' in response.json()
