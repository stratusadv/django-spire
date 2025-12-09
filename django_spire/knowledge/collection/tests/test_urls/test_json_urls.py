from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection


class CollectionJsonUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.test_collection = create_test_collection()

    def test_reorder_view_url_path(self):
        response = self.client.post(
            reverse('django_spire:knowledge:collection:json:reorder'),
            data={
                'collection_id': self.test_collection.pk,
                'order': 0
            },
            content_type='application/json',
        )
        assert response.status_code == 200

    def test_reorder_view_with_parent(self):
        child_collection = create_test_collection(
            parent=self.test_collection,
            name='Child Collection'
        )
        response = self.client.post(
            reverse('django_spire:knowledge:collection:json:reorder'),
            data={
                'collection_id': child_collection.pk,
                'order': 0,
                'parent': self.test_collection.pk
            },
            content_type='application/json',
        )
        assert response.status_code == 200

    def test_reorder_view_invalid_collection(self):
        response = self.client.post(
            reverse('django_spire:knowledge:collection:json:reorder'),
            data={
                'collection_id': 99999,
                'order': 0
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.json()['type'] == 'error'

    def test_reorder_view_missing_order(self):
        response = self.client.post(
            reverse('django_spire:knowledge:collection:json:reorder'),
            data={
                'collection_id': self.test_collection.pk,
            },
            content_type='application/json',
        )
        assert response.status_code == 200
        assert response.json()['type'] == 'error'
