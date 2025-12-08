from __future__ import annotations

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class AuthUserServiceTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user1 = create_user(
            username='user1',
            first_name='Alice',
            last_name='Smith',
            is_active=True
        )
        self.user2 = create_user(
            username='user2',
            first_name='Bob',
            last_name='Jones',
            is_active=True
        )
        self.inactive_user = create_user(
            username='inactive',
            first_name='Charlie',
            last_name='Brown',
            is_active=False
        )

    def test_get_user_choices_returns_list(self) -> None:
        choices = AuthUser.services.get_user_choices()
        assert isinstance(choices, list) is True

    def test_get_user_choices_format(self) -> None:
        choices = AuthUser.services.get_user_choices()
        for choice in choices:
            assert len(choice) == 2
            assert isinstance(choice[0], int) is True
            assert isinstance(choice[1], str) is True

    def test_get_user_choices_excludes_inactive(self) -> None:
        choices = AuthUser.services.get_user_choices()
        user_ids = [c[0] for c in choices]
        assert self.inactive_user.pk not in user_ids

    def test_get_user_choices_includes_active(self) -> None:
        choices = AuthUser.services.get_user_choices()
        user_ids = [c[0] for c in choices]
        assert self.user1.pk in user_ids
        assert self.user2.pk in user_ids

    def test_get_user_choices_by_group(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        self.user1.groups.add(group)

        choices = AuthUser.services.get_user_choices_by_group(group)
        user_ids = [c[0] for c in choices]

        assert self.user1.pk in user_ids
        assert self.user2.pk not in user_ids

    def test_get_user_choices_by_group_empty(self) -> None:
        group = AuthGroup.objects.create(name='Empty Group')
        choices = AuthUser.services.get_user_choices_by_group(group)
        assert len(choices) == 0

    def test_get_user_choices_by_group_multiple_users(self) -> None:
        group = AuthGroup.objects.create(name='Multi User Group')
        self.user1.groups.add(group)
        self.user2.groups.add(group)

        choices = AuthUser.services.get_user_choices_by_group(group)
        user_ids = [c[0] for c in choices]

        assert self.user1.pk in user_ids
        assert self.user2.pk in user_ids

    def test_get_user_choices_by_group_excludes_inactive(self) -> None:
        group = AuthGroup.objects.create(name='Mixed Group')
        self.user1.groups.add(group)
        self.inactive_user.groups.add(group)

        choices = AuthUser.services.get_user_choices_by_group(group)
        user_ids = [c[0] for c in choices]

        assert self.user1.pk in user_ids
        assert self.inactive_user.pk not in user_ids

    def test_get_user_choices_returns_full_name(self) -> None:
        choices = AuthUser.services.get_user_choices()
        user1_choice = next((c for c in choices if c[0] == self.user1.pk), None)
        assert user1_choice is not None
        assert user1_choice[1] == 'Alice Smith'

    def test_get_user_choices_with_no_active_users(self) -> None:
        AuthUser.objects.filter(is_active=True).update(is_active=False)
        choices = AuthUser.services.get_user_choices()
        assert len(choices) == 0

    def test_get_user_choices_user_in_multiple_groups(self) -> None:
        group1 = AuthGroup.objects.create(name='Group 1')
        group2 = AuthGroup.objects.create(name='Group 2')
        self.user1.groups.add(group1, group2)

        choices1 = AuthUser.services.get_user_choices_by_group(group1)
        choices2 = AuthUser.services.get_user_choices_by_group(group2)

        assert any(c[0] == self.user1.pk for c in choices1)
        assert any(c[0] == self.user1.pk for c in choices2)
