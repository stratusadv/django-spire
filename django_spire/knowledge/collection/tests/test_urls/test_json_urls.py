from django.urls import reverse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.tests.factories import create_test_collection


class CollectionJsonUrlsTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.test_collection = create_test_collection()

    def test_reorder_view_url_path(self):
        response = self.client.post(
            reverse(
                'django_spire:knowledge:collection:json:reorder',
                kwargs={'pk': self.test_collection.pk}
            ),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)