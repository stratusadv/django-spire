from __future__ import annotations

# import json

from django.contrib.sites.models import Site
# from django.conf import settings
# from django.test import RequestFactory

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.tests.factories import create_test_collection


class CollectionServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.collection = create_test_collection()

    def test_save_model_obj_creates_new(self):
        collection, created = Collection.services.save_model_obj(
            name='New Collection',
            description='A new collection'
        )
        assert created is True
        assert collection.name == 'New Collection'

    def test_save_model_obj_updates_existing(self):
        self.collection.services.obj = self.collection
        updated_collection, created = self.collection.services.save_model_obj(
            name='Updated Name'
        )
        assert created is False
        assert updated_collection.name == 'Updated Name'


class CollectionOrderingServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.parent = create_test_collection(name='Parent')
        self.child1 = create_test_collection(parent=self.parent, name='Child 1')
        self.child2 = create_test_collection(parent=self.parent, name='Child 2')

    def test_reorder_within_same_parent(self):
        self.child2.services.ordering.reorder(order=0, new_parent_pk=self.parent.pk)
        self.child1.refresh_from_db()
        self.child2.refresh_from_db()
        assert self.child2.order <= self.child1.order

    def test_reorder_to_new_parent(self):
        new_parent = create_test_collection(name='New Parent')
        self.child1.services.ordering.reorder(order=0, new_parent_pk=new_parent.pk)
        self.child1.refresh_from_db()
        assert self.child1.parent_id == new_parent.pk

    def test_reorder_to_root(self):
        self.child1.services.ordering.reorder(order=0, new_parent_pk=None)
        self.child1.refresh_from_db()
        assert self.child1.parent_id is None


class CollectionProcessorServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.parent = create_test_collection(name='Parent')
        self.child = create_test_collection(parent=self.parent, name='Child')

    def test_set_deleted(self):
        self.parent.services.processor.set_deleted()
        self.parent.refresh_from_db()
        assert self.parent.is_deleted is True

    def test_set_deleted_cascades_to_children(self):
        self.parent.services.processor.set_deleted()
        self.child.refresh_from_db()
        assert self.child.is_deleted is True


class CollectionToolServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.parent = create_test_collection(name='Parent')
        self.child = create_test_collection(parent=self.parent, name='Child')
        self.grandchild = create_test_collection(parent=self.child, name='Grandchild')

    def test_get_children_ids(self):
        children_ids = Collection.services.tool.get_children_ids(parent_id=self.parent.pk)
        assert self.child.pk in children_ids
        assert self.grandchild.pk in children_ids
        assert self.parent.pk not in children_ids

    def test_get_root_collection_pk(self):
        self.grandchild.services.tool.obj = self.grandchild
        root_pk = self.grandchild.services.tool.get_root_collection_pk()
        assert root_pk == self.parent.pk

    def test_get_root_collection_pk_when_already_root(self):
        self.parent.services.tool.obj = self.parent
        root_pk = self.parent.services.tool.get_root_collection_pk()
        assert root_pk == self.parent.pk


class TestCollectionTransformationService(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.site = Site.objects.create(domain='', name='')

    def _test_collection_urls_json(self, collection_json: dict):
        response = self.client.get(collection_json['delete_url'].replace(' ', ''))
        assert response.status_code == 200

        response = self.client.get(collection_json['create_entry_url'].replace(' ', ''))
        assert response.status_code == 200

        response = self.client.get(collection_json['import_entry_url'].replace(' ', ''))
        assert response.status_code == 200

    # # TODO(Tyrell): Talk to Chase about this
    # def test_to_hierarchy_json(self):
    #     settings.SITE_ID = self.site.id

    #     self.test_collection_1 = Collection.objects.create(name='Grand Parent A', id=1, parent_id=None)
    #     self.test_collection_2 = Collection.objects.create(name='Parent A1', id=2, parent_id=1)
    #     self.test_collection_3 = Collection.objects.create(name='Child A1a', id=3, parent_id=2)

    #     request = RequestFactory().get('/')
    #     request.user = self.super_user

    #     family_tree = Collection.services.transformation.to_hierarchy_json(
    #         request=request
    #     )

    #     for collection_json in json.loads(family_tree):
    #         assert collection_json['id'] is not None
    #         assert collection_json['name'] == 'Grand Parent A'

    #         assert len(collection_json['entries']) == 0

    #         self._test_collection_urls_json(collection_json=collection_json)

    #         assert len(collection_json['children']) == 1

    #         for child_json in collection_json['children']:
    #             assert child_json['id'] is not None
    #             assert child_json['name'] == 'Parent A1'

    #             assert len(child_json['entries']) == 0

    #             self._test_collection_urls_json(collection_json=child_json)

    #             assert len(child_json['children']) == 1

    #             for grand_child_json in child_json['children']:
    #                 assert grand_child_json['id'] is not None
    #                 assert grand_child_json['name'] == 'Child A1a'

    #                 assert len(grand_child_json['entries']) == 0

    #                 self._test_collection_urls_json(collection_json=grand_child_json)

    #                 assert len(grand_child_json['children']) == 0
