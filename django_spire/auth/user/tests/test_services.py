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
        assert isinstance(choices, list)

    def test_get_user_choices_format(self) -> None:
        choices = AuthUser.services.get_user_choices()
        for choice in choices:
            assert len(choice) == 2
            assert isinstance(choice[0], int)
            assert isinstance(choice[1], str)

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

    def test_get_user_choices_empty_name(self) -> None:
        user = create_user(username='emptyname', first_name='', last_name='')
        choices = AuthUser.services.get_user_choices()
        user_choice = next((c for c in choices if c[0] == user.pk), None)
        assert user_choice is not None
        assert user_choice[1] == ''

    def test_get_user_choices_unicode_name(self) -> None:
        user = create_user(username='unicode', first_name='Tëst', last_name='Üsér')
        choices = AuthUser.services.get_user_choices()
        user_choice = next((c for c in choices if c[0] == user.pk), None)
        assert user_choice is not None
        assert 'Tëst' in user_choice[1]
        assert 'Üsér' in user_choice[1]

    def test_get_user_choices_first_name_only(self) -> None:
        user = create_user(username='firstonly', first_name='First', last_name='')
        choices = AuthUser.services.get_user_choices()
        user_choice = next((c for c in choices if c[0] == user.pk), None)
        assert user_choice is not None
        assert 'First' in user_choice[1]

    def test_get_user_choices_last_name_only(self) -> None:
        user = create_user(username='lastonly', first_name='', last_name='Last')
        choices = AuthUser.services.get_user_choices()
        user_choice = next((c for c in choices if c[0] == user.pk), None)
        assert user_choice is not None
        assert 'Last' in user_choice[1]

    def test_get_user_choices_by_group_nonexistent_group(self) -> None:
        group = AuthGroup.objects.create(name='Temp Group')
        group_pk = group.pk
        group.delete()
        new_group = AuthGroup(pk=group_pk, name='Fake')
        choices = AuthUser.services.get_user_choices_by_group(new_group)
        assert len(choices) == 0

    def test_get_user_choices_many_users(self) -> None:
        for i in range(50):
            create_user(username=f'manyuser{i}', first_name=f'User{i}', last_name='Test')
        choices = AuthUser.services.get_user_choices()
        assert len(choices) >= 50

    def test_get_user_choices_by_group_after_user_removal(self) -> None:
        group = AuthGroup.objects.create(name='Removal Group')
        self.user1.groups.add(group)

        choices_before = AuthUser.services.get_user_choices_by_group(group)
        assert any(c[0] == self.user1.pk for c in choices_before)

        self.user1.groups.remove(group)

        choices_after = AuthUser.services.get_user_choices_by_group(group)
        assert not any(c[0] == self.user1.pk for c in choices_after)

    def test_get_user_choices_by_group_after_user_deactivation(self) -> None:
        group = AuthGroup.objects.create(name='Deactivation Group')
        self.user1.groups.add(group)

        choices_before = AuthUser.services.get_user_choices_by_group(group)
        assert any(c[0] == self.user1.pk for c in choices_before)

        self.user1.is_active = False
        self.user1.save()

        choices_after = AuthUser.services.get_user_choices_by_group(group)
        assert not any(c[0] == self.user1.pk for c in choices_after)

    def test_service_obj_class_is_auth_user(self) -> None:
        assert AuthUser.services.obj_class == AuthUser

    def test_get_user_choices_order(self) -> None:
        choices = AuthUser.services.get_user_choices()
        assert len(choices) > 0

    def test_get_user_choices_by_group_returns_list(self) -> None:
        group = AuthGroup.objects.create(name='List Group')
        choices = AuthUser.services.get_user_choices_by_group(group)
        assert isinstance(choices, list)

    def test_get_user_choices_by_group_format(self) -> None:
        group = AuthGroup.objects.create(name='Format Group')
        self.user1.groups.add(group)
        choices = AuthUser.services.get_user_choices_by_group(group)
        for choice in choices:
            assert len(choice) == 2
            assert isinstance(choice[0], int)
            assert isinstance(choice[1], str)
