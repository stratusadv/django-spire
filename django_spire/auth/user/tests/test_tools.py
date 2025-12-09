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
        assert Group.objects.filter(name='All Users').exists()

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

    def test_user_not_added_to_other_groups(self) -> None:
        other_group = Group.objects.create(name='Other Group')
        add_user_to_all_user_group(self.user)
        assert self.user not in other_group.user_set.all()

    def test_multiple_calls_single_group_entry(self) -> None:
        for _ in range(5):
            add_user_to_all_user_group(self.user)
        group = Group.objects.get(name='All Users')
        assert group.user_set.filter(pk=self.user.pk).count() == 1

    def test_group_persists_after_function_call(self) -> None:
        Group.objects.filter(name='All Users').delete()
        add_user_to_all_user_group(self.user)
        assert Group.objects.filter(name='All Users').exists()

    def test_user_membership_persists(self) -> None:
        add_user_to_all_user_group(self.user)
        self.user.refresh_from_db()
        group = Group.objects.get(name='All Users')
        assert group in self.user.groups.all()

    def test_does_not_remove_existing_members(self) -> None:
        existing_user = create_user(username='existinguser')
        group = Group.objects.create(name='All Users')
        group.user_set.add(existing_user)

        add_user_to_all_user_group(self.user)

        assert existing_user in group.user_set.all()
        assert self.user in group.user_set.all()

    def test_works_with_staff_user(self) -> None:
        staff_user = create_user(username='staffuser', is_staff=True)
        add_user_to_all_user_group(staff_user)
        group = Group.objects.get(name='All Users')
        assert staff_user in group.user_set.all()

    def test_works_with_superuser(self) -> None:
        superuser = create_user(username='superuser', is_superuser=True)
        add_user_to_all_user_group(superuser)
        group = Group.objects.get(name='All Users')
        assert superuser in group.user_set.all()

    def test_case_sensitive_group_name(self) -> None:
        Group.objects.create(name='all users')
        Group.objects.filter(name='All Users').delete()
        add_user_to_all_user_group(self.user)
        assert Group.objects.filter(name='All Users').exists()
        assert Group.objects.filter(name='all users').exists()

    def test_many_users_added(self) -> None:
        users = [create_user(username=f'manyuser{i}') for i in range(20)]
        for user in users:
            add_user_to_all_user_group(user)
        group = Group.objects.get(name='All Users')
        for user in users:
            assert user in group.user_set.all()

    def test_user_groups_query(self) -> None:
        add_user_to_all_user_group(self.user)
        groups = self.user.groups.all()
        group_names = [g.name for g in groups]
        assert 'All Users' in group_names

    def test_group_user_count_increments(self) -> None:
        Group.objects.filter(name='All Users').delete()
        group = Group.objects.create(name='All Users')
        initial_count = group.user_set.count()

        add_user_to_all_user_group(self.user)
        group.refresh_from_db()

        assert group.user_set.count() == initial_count + 1

    def test_does_not_create_duplicate_groups(self) -> None:
        Group.objects.filter(name='All Users').delete()
        user1 = create_user(username='user1')
        user2 = create_user(username='user2')

        add_user_to_all_user_group(user1)
        add_user_to_all_user_group(user2)

        assert Group.objects.filter(name='All Users').count() == 1
