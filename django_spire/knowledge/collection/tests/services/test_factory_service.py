import json

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.models import Collection


class TestCollectionTransformationService(BaseTestCase):
    def test_to_hierarchy_json(self):
        Collection.objects.bulk_create([
            Collection(name='Grand Parent A', id=1, parent_id=None),
            Collection(name='Parent A1', id=2, parent_id=1),
            Collection(name='Child A1a', id=3, parent_id=2),
            Collection(name='Parent A2', id=4, parent_id=1),
            Collection(name='Child A2a', id=5, parent_id=4),
            Collection(name='Child A2b', id=6, parent_id=4),
            Collection(name='Grand Parent B', id=7, parent_id=None),
            Collection(name='Parent B1', id=8, parent_id=7),
            Collection(name='Child B1a', id=9, parent_id=8),
            Collection(name='Grand Child B1a1', id=10, parent_id=9),
        ])

        family_tree = Collection.services.transformation.to_hierarchy_json(
            queryset=Collection.objects.all().select_related('parent')
        )

        expected_family_tree = [
            {
                'id': 1,
                'name': 'Grand Parent A',
                'description': '',
                'children': [
                    {
                        'id': 2,
                        'name': 'Parent A1',
                        'description': '',
                        'children': [
                            {
                                'id': 3,
                                'name': 'Child A1a',
                                'description': '',
                                'children': [],
                            }
                        ],
                    },
                    {
                        'id': 4,
                        'name': 'Parent A2',
                        'description': '',
                        'children': [
                            {
                                'id': 5,
                                'name': 'Child A2a',
                                'description': '',
                                'children': [],
                            },
                            {
                                'id': 6,
                                'name': 'Child A2b',
                                'description': '',
                                'children': [],
                            }
                        ],
                    }
                ],
            },
            {
                'id': 7,
                'name': 'Grand Parent B',
                'description': '',
                'children': [
                    {
                        'id': 8,
                        'name': 'Parent B1',
                        'description': '',
                        'children': [
                            {
                                'id': 9,
                                'name': 'Child B1a',
                                'description': '',
                                'children': [
                                    {
                                        'id': 10,
                                        'name': 'Grand Child B1a1',
                                        'description': '',
                                        'children': [],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]

        self.assertEqual(
            json.loads(family_tree),
            expected_family_tree,
        )
