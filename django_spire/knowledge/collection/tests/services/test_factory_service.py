import json

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.models import Collection


class TestCollectionTransformationService(BaseTestCase):
    def test_to_hierarchy_json(self):
        self.test_collection_1 = Collection.objects.create(name='Grand Parent A', id=1, parent_id=None)
        self.test_collection_2 = Collection.objects.create(name='Parent A1', id=2, parent_id=1)
        self.test_collection_3 = Collection.objects.create(name='Child A1a', id=3, parent_id=2)

        family_tree = Collection.services.transformation.to_hierarchy_json(
            queryset=Collection.objects.all().select_related('parent'),
            user=self.super_user
        )

        expected_family_tree = [
            {
                'id': 1,
                'delete_url': self.test_collection_1.delete_url,
                'create_entry_url': self.test_collection_1.create_entry_url,
                'import_entry_url': self.test_collection_1.import_entry_url,
                'name': 'Grand Parent A',
                'description': '',
                'entries': [],
                'children': [
                    {
                        'id': 2,
                        'delete_url': self.test_collection_2.delete_url,
                        'create_entry_url': self.test_collection_2.create_entry_url,
                        'import_entry_url': self.test_collection_2.import_entry_url,
                        'name': 'Parent A1',
                        'description': '',
                        'entries': [],
                        'children': [
                            {
                                'id': 3,
                                'delete_url': self.test_collection_3.delete_url,
                                'create_entry_url': self.test_collection_3.create_entry_url,
                                'import_entry_url': self.test_collection_3.import_entry_url,
                                'name': 'Child A1a',
                                'description': '',
                                'entries': [],
                                'children': [],
                            }
                        ],
                    }
                ]
            }
            ]

        self.assertEqual(
            json.loads(family_tree),
            expected_family_tree,
        )
