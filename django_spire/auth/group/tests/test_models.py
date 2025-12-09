from __future__ import annotations

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class AuthGroupModelTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group = AuthGroup.objects.create(name='Test Group')

    def test_str_representation(self) -> None:
        assert str(self.group) == 'Test Group'

    def test_str_representation_with_special_characters(self) -> None:
        group = AuthGroup.objects.create(name='Test & Group <Special>')
        assert str(group) == 'Test & Group <Special>'

    def test_base_breadcrumb_returns_breadcrumbs(self) -> None:
        crumbs = AuthGroup.base_breadcrumb()
        assert crumbs is not None

    def test_breadcrumbs_with_pk_returns_breadcrumbs(self) -> None:
        crumbs = self.group.breadcrumbs()
        assert crumbs is not None

    def test_breadcrumbs_without_pk_returns_breadcrumbs(self) -> None:
        unsaved_group = AuthGroup(name='Unsaved Group')
        crumbs = unsaved_group.breadcrumbs()
        assert crumbs is not None

    def test_meta_proxy(self) -> None:
        assert AuthGroup._meta.proxy

    def test_meta_verbose_name(self) -> None:
        assert AuthGroup._meta.verbose_name == 'Auth Group'
        assert AuthGroup._meta.verbose_name_plural == 'Auth Groups'

    def test_group_creation(self) -> None:
        group = AuthGroup.objects.create(name='New Test Group')
        assert group.pk is not None
        assert AuthGroup.objects.filter(pk=group.pk).exists()

    def test_group_update(self) -> None:
        self.group.name = 'Updated Group Name'
        self.group.save()
        self.group.refresh_from_db()
        assert self.group.name == 'Updated Group Name'

    def test_group_deletion(self) -> None:
        group_pk = self.group.pk
        self.group.delete()
        assert not AuthGroup.objects.filter(pk=group_pk).exists()

    def test_group_user_relationship(self) -> None:
        user = create_user(username='groupuser')
        self.group.user_set.add(user)
        assert user in self.group.user_set.all()
        assert self.group in user.groups.all()

    def test_group_permissions_relationship(self) -> None:
        assert hasattr(self.group, 'permissions')

    def test_group_name_max_length(self) -> None:
        max_length = AuthGroup._meta.get_field('name').max_length
        assert max_length == 150

    def test_multiple_groups_creation(self) -> None:
        groups = [
            AuthGroup.objects.create(name=f'Group {i}')
            for i in range(5)
        ]
        assert len(groups) == 5
        assert AuthGroup.objects.count() >= 5

    def test_group_queryset_ordering(self) -> None:
        AuthGroup.objects.create(name='Zebra Group')
        AuthGroup.objects.create(name='Alpha Group')
        groups = AuthGroup.objects.all().order_by('name')
        names = list(groups.values_list('name', flat=True))
        assert names == sorted(names)

    def test_group_add_multiple_users(self) -> None:
        user1 = create_user(username='user1')
        user2 = create_user(username='user2')
        self.group.user_set.add(user1, user2)
        assert self.group.user_set.count() == 2

    def test_group_remove_user(self) -> None:
        user = create_user(username='removeuser')
        self.group.user_set.add(user)
        self.group.user_set.remove(user)
        assert user not in self.group.user_set.all()

    def test_group_clear_users(self) -> None:
        user1 = create_user(username='clearuser1')
        user2 = create_user(username='clearuser2')
        self.group.user_set.add(user1, user2)
        self.group.user_set.clear()
        assert self.group.user_set.count() == 0

    def test_group_add_permission(self) -> None:
        content_type = ContentType.objects.get_for_model(AuthGroup)
        permission = Permission.objects.filter(content_type=content_type).first()
        if permission:
            self.group.permissions.add(permission)
            assert permission in self.group.permissions.all()

    def test_group_remove_permission(self) -> None:
        content_type = ContentType.objects.get_for_model(AuthGroup)
        permission = Permission.objects.filter(content_type=content_type).first()
        if permission:
            self.group.permissions.add(permission)
            self.group.permissions.remove(permission)
            assert permission not in self.group.permissions.all()

    def test_group_with_unicode_name(self) -> None:
        group = AuthGroup.objects.create(name='Tëst Grøup 日本語')
        assert group.name == 'Tëst Grøup 日本語'
        assert str(group) == 'Tëst Grøup 日本語'

    def test_group_name_with_max_length(self) -> None:
        long_name = 'A' * 150
        group = AuthGroup.objects.create(name=long_name)
        assert group.name == long_name

    def test_breadcrumbs_contains_group_name(self) -> None:
        crumbs = self.group.breadcrumbs()
        names = [c['name'] for c in crumbs]
        assert 'Test Group' in names

    def test_base_breadcrumb_contains_groups(self) -> None:
        crumbs = AuthGroup.base_breadcrumb()
        names = [c['name'] for c in crumbs]
        assert 'Groups' in names

    def test_group_user_set_query(self) -> None:
        user = create_user(username='queryuser')
        self.group.user_set.add(user)
        queried_users = self.group.user_set.filter(username='queryuser')
        assert queried_users.count() == 1

    def test_group_inheritance_from_django_group(self) -> None:
        from django.contrib.auth.models import Group
        assert issubclass(AuthGroup, Group)

    def test_group_activity_mixin(self) -> None:
        assert hasattr(self.group, 'add_activity')

    def test_group_empty_name_constraint(self) -> None:
        group = AuthGroup.objects.create(name='')
        assert group.pk is not None

    def test_group_whitespace_name(self) -> None:
        group = AuthGroup.objects.create(name='   ')
        assert group.name == '   '

    def test_group_special_characters_name(self) -> None:
        special_name = '!@#$%^&*()_+-=[]{}|;:,.<>?'
        group = AuthGroup.objects.create(name=special_name)
        assert group.name == special_name

    def test_group_refresh_from_db(self) -> None:
        original_name = self.group.name
        AuthGroup.objects.filter(pk=self.group.pk).update(name='Changed Name')
        self.group.refresh_from_db()
        assert self.group.name == 'Changed Name'
        assert self.group.name != original_name

    def test_group_get_or_create(self) -> None:
        group, created = AuthGroup.objects.get_or_create(name='Get Or Create Group')
        assert created
        group2, created2 = AuthGroup.objects.get_or_create(name='Get Or Create Group')
        assert not created2
        assert group.pk == group2.pk

    def test_group_bulk_create(self) -> None:
        groups = AuthGroup.objects.bulk_create([
            AuthGroup(name='Bulk 1'),
            AuthGroup(name='Bulk 2'),
            AuthGroup(name='Bulk 3'),
        ])
        assert len(groups) == 3

    def test_group_exists(self) -> None:
        assert AuthGroup.objects.filter(name='Test Group').exists()
        assert not AuthGroup.objects.filter(name='Nonexistent Group').exists()
