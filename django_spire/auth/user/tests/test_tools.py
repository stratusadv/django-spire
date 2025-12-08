from __future__ import annotations

from django.contrib.auth.models import Group

from django_spire.auth.user.tests.factories import create_user
from django_spire.auth.user.tools import add_user_to_all_user_group
from django_spire.core.tests.test_cases import BaseTestCase


class AddUserToAllUserGroupTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser')

    def test_creates_all_users_group_if_not_exists(self) -> None:
        Group.objects.filter(name='All Users').delete()
        add_user_to_all_user_group(self.user)
        assert Group.objects.filter(name='All Users').exists() is True

    def test_adds_user_to_existing_group(self) -> None:
        group = Group.objects.create(name='All Users')
        add_user_to_all_user_group(self.user)
        assert self.user in group.user_set.all()

    def test_user_in_all_users_group(self) -> None:
        add_user_to_all_user_group(self.user)
        group = Group.objects.get(name='All Users')
        assert self.user in group.user_set.all()

    def test_idempotent_add(self) -> None:
        add_user_to_all_user_group(self.user)
        add_user_to_all_user_group(self.user)
        group = Group.objects.get(name='All Users')
        assert group.user_set.filter(pk=self.user.pk).count() == 1

    def test_multiple_users_added(self) -> None:
        user2 = create_user(username='testuser2')
        add_user_to_all_user_group(self.user)
        add_user_to_all_user_group(user2)
        group = Group.objects.get(name='All Users')
        assert group.user_set.count() >= 2
        assert self.user in group.user_set.all()
        assert user2 in group.user_set.all()

    def test_user_remains_in_other_groups(self) -> None:
        other_group = Group.objects.create(name='Other Group')
        self.user.groups.add(other_group)
        add_user_to_all_user_group(self.user)
        assert other_group in self.user.groups.all()

    def test_group_created_with_exact_name(self) -> None:
        Group.objects.filter(name='All Users').delete()
        add_user_to_all_user_group(self.user)
        group = Group.objects.get(name='All Users')
        assert group.name == 'All Users'

    def test_inactive_user_can_be_added(self) -> None:
        inactive_user = create_user(username='inactive', is_active=False)
        add_user_to_all_user_group(inactive_user)
        group = Group.objects.get(name='All Users')
        assert inactive_user in group.user_set.all()

    def test_does_not_affect_other_groups(self) -> None:
        other_group = Group.objects.create(name='Other Group')
        initial_count = other_group.user_set.count()
        add_user_to_all_user_group(self.user)
        assert other_group.user_set.count() == initial_count
