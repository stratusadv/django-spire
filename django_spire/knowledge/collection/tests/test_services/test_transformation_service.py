import json

from django.contrib.sites.models import Site
from django.conf import settings

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.models import Collection


class TestCollectionTransformationService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.site = Site.objects.create(domain='', name='')

    def _test_collection_urls_json(self, collection_json: dict):
        response = self.client.get(collection_json['delete_url'].replace(' ', ''))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(collection_json['create_entry_url'].replace(' ', ''))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(collection_json['import_entry_url'].replace(' ', ''))
        self.assertEqual(response.status_code, 200)

    def test_to_hierarchy_json(self):
        settings.SITE_ID = self.site.id

        self.test_collection_1 = Collection.objects.create(name='Grand Parent A', id=1, parent_id=None)
        self.test_collection_2 = Collection.objects.create(name='Parent A1', id=2, parent_id=1)
        self.test_collection_3 = Collection.objects.create(name='Child A1a', id=3, parent_id=2)

        family_tree = Collection.services.transformation.to_hierarchy_json(
            user=self.super_user
        )

        for collection_json in json.loads(family_tree):
            self.assertIsNotNone(collection_json['id'])
            self.assertEqual(collection_json['name'], 'Grand Parent A')

            self.assertEqual(len(collection_json['entries']), 0)

            self._test_collection_urls_json(collection_json=collection_json)

            self.assertEqual(len(collection_json['children']), 1)

            for child_json in collection_json['children']:
                self.assertIsNotNone(child_json['id'])
                self.assertEqual(child_json['name'], 'Parent A1')

                self.assertEqual(len(child_json['entries']), 0)

                self._test_collection_urls_json(collection_json=child_json)

                self.assertEqual(len(child_json['children']), 1)

                for grand_child_json in child_json['children']:
                    self.assertIsNotNone(grand_child_json['id'])
                    self.assertEqual(grand_child_json['name'], 'Child A1a')

                    self.assertEqual(len(grand_child_json['entries']), 0)

                    self._test_collection_urls_json(collection_json=grand_child_json)

                    self.assertEqual(len(grand_child_json['children']), 0)
