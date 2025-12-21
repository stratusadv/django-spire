from __future__ import annotations

from django.test import RequestFactory

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.tests.factories import (
    create_test_auth_group,
    create_test_collection,
    create_test_collection_group,
)


class CollectionQuerySetTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = create_user(username='test_queryset_user')
        self.parent_collection = create_test_collection(name='Parent')
        self.child_collection = create_test_collection(
            parent=self.parent_collection,
            name='Child'
        )

    def test_by_parent(self):
        result = Collection.objects.by_parent(parent=self.parent_collection)
        assert self.child_collection in result
        assert self.parent_collection not in result

    def test_by_parent_id(self):
        result = Collection.objects.by_parent_id(parent_id=self.parent_collection.id)
        assert self.child_collection in result

    def test_by_parent_ids(self):
        result = Collection.objects.by_parent_ids(parent_ids=[self.parent_collection.id])
        assert self.child_collection in result

    def test_parentless(self):
        result = Collection.objects.parentless()
        assert self.parent_collection in result
        assert self.child_collection not in result

    def test_childless(self):
        grandchild = create_test_collection(
            parent=self.child_collection,
            name='Grandchild'
        )
        result = Collection.objects.childless()
        assert grandchild in result
        assert self.parent_collection not in result

    def test_children(self):
        grandchild = create_test_collection(
            parent=self.child_collection,
            name='Grandchild'
        )
        result = Collection.objects.children(collection_id=self.parent_collection.id)
        assert self.child_collection in result
        assert grandchild in result

    def test_exclude_children(self):
        grandchild = create_test_collection(
            parent=self.child_collection,
            name='Grandchild'
        )
        result = Collection.objects.exclude_children(collection_id=self.parent_collection.id)
        assert self.parent_collection in result
        assert self.child_collection not in result
        assert grandchild not in result

    def test_annotate_entry_count(self):
        result = Collection.objects.annotate_entry_count()
        assert result.first().entry_count == 0

    def test_request_user_has_access_superuser(self):
        request = self.factory.get('/')
        request.user = self.super_user
        result = Collection.objects.request_user_has_access(request)
        assert self.parent_collection in result

    def test_request_user_has_access_with_group(self):
        auth_group = create_test_auth_group(name='Access Group')
        self.user.groups.add(auth_group)
        create_test_collection_group(
            collection=self.parent_collection,
            auth_group=auth_group
        )

        request = self.factory.get('/')
        request.user = self.user
        result = Collection.objects.request_user_has_access(request)
        assert self.parent_collection in result
