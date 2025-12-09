from __future__ import annotations

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.knowledge.collection.models import Collection, CollectionGroup
from django_spire.knowledge.collection.tests.factories import (
    create_test_auth_group,
    create_test_collection,
    create_test_collection_group,
)


class CollectionGroupFactoryServiceTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = create_user(username='test_factory_user')
        self.collection = create_test_collection()
        self.auth_group1 = create_test_auth_group(name='Group 1')
        self.auth_group2 = create_test_auth_group(name='Group 2')

        content_type = ContentType.objects.get_for_model(Collection)
        self.change_groups_permission = Permission.objects.get(
            codename='can_change_collection_groups',
            content_type=content_type
        )

    def _refresh_user(self):
        self.user = type(self.user).objects.get(pk=self.user.pk)

    def test_replace_groups_without_permission(self):
        request = self.factory.get('/')
        request.user = self.user

        result = CollectionGroup.services.factory.replace_groups(
            request=request,
            group_pks=[self.auth_group1.pk],
            collection=self.collection
        )
        assert result == []

    def test_replace_groups_with_permission(self):
        self.user.user_permissions.add(self.change_groups_permission)
        self._refresh_user()

        request = self.factory.get('/')
        request.user = self.user

        result = CollectionGroup.services.factory.replace_groups(
            request=request,
            group_pks=[self.auth_group1.pk, self.auth_group2.pk],
            collection=self.collection
        )
        assert len(result) == 2
        assert self.collection.groups.count() == 2

    def test_replace_groups_removes_old(self):
        self.user.user_permissions.add(self.change_groups_permission)
        self._refresh_user()

        create_test_collection_group(
            collection=self.collection,
            auth_group=self.auth_group1
        )

        request = self.factory.get('/')
        request.user = self.user

        CollectionGroup.services.factory.replace_groups(
            request=request,
            group_pks=[self.auth_group2.pk],
            collection=self.collection
        )

        assert self.collection.groups.count() == 1
        assert self.collection.groups.first().auth_group == self.auth_group2

    def test_replace_groups_with_none_deletes_all(self):
        self.user.user_permissions.add(self.change_groups_permission)
        self._refresh_user()

        create_test_collection_group(
            collection=self.collection,
            auth_group=self.auth_group1
        )

        request = self.factory.get('/')
        request.user = self.user

        CollectionGroup.services.factory.replace_groups(
            request=request,
            group_pks=None,
            collection=self.collection
        )

        assert self.collection.groups.count() == 0
