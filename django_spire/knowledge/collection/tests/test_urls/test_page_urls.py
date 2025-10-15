from __future__ import annotations

from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection


class CollectionPageUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.test_collection = create_test_collection()

    def test_delete_view_url_path(self):
        response = self.client.get(
            reverse(
                'django_spire:knowledge:collection:page:delete',
                kwargs={'pk': self.test_collection.pk}
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_list_view_url_path(self):
        response = self.client.get(
            reverse('django_spire:knowledge:collection:page:list')
        )

        self.assertEqual(response.status_code, 200)
