from __future__ import annotations

import pytest

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.group.utils import (
    codename_list_to_perm_level,
    codename_to_perm_level,
    has_app_permission,
    has_app_permission_or_404,
    perm_level_to_django_permission,
    perm_level_to_int,
    perm_level_to_string,
    set_group_users,
)
from django_spire.auth.user.tests.factories import create_super_user, create_user
from django_spire.core.tests.test_cases import BaseTestCase


class SetGroupUsersTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group = AuthGroup.objects.create(name='Test Group')
        self.user1 = create_user(username='user1')
        self.user2 = create_user(username='user2')
        self.user3 = create_user(username='user3')

    def test_set_group_users(self) -> None:
        set_group_users(self.group, [self.user1, self.user2])
        assert self.group.user_set.count() == 2

    def test_set_group_users_empty(self) -> None:
        self.group.user_set.add(self.user1)
        set_group_users(self.group, [])
        assert self.group.user_set.count() == 0

    def test_set_group_users_replaces_existing(self) -> None:
        self.group.user_set.add(self.user1)
        set_group_users(self.group, [self.user2])
        assert self.group.user_set.count() == 1
        assert self.user2 in self.group.user_set.all()
        assert self.user1 not in self.group.user_set.all()

    def test_set_group_users_multiple(self) -> None:
        set_group_users(self.group, [self.user1, self.user2, self.user3])
        assert self.group.user_set.count() == 3

    def test_set_group_users_idempotent(self) -> None:
        set_group_users(self.group, [self.user1])
        set_group_users(self.group, [self.user1])
        assert self.group.user_set.count() == 1

    def test_set_group_users_preserves_user_in_other_groups(self) -> None:
        other_group = AuthGroup.objects.create(name='Other Group')
        other_group.user_set.add(self.user1)
        set_group_users(self.group, [self.user1])
        assert self.user1 in other_group.user_set.all()
        assert self.user1 in self.group.user_set.all()


class CodenameToPermLevelTestCase(BaseTestCase):
    def test_view_codename(self) -> None:
        assert codename_to_perm_level('view_model') == 1

    def test_add_codename(self) -> None:
        assert codename_to_perm_level('add_model') == 2

    def test_change_codename(self) -> None:
        assert codename_to_perm_level('change_model') == 3

    def test_delete_codename(self) -> None:
        assert codename_to_perm_level('delete_model') == 4

    def test_none_codename(self) -> None:
        assert codename_to_perm_level('none_model') == 0

    def test_unknown_prefix(self) -> None:
        assert codename_to_perm_level('unknown_model') == 0

    def test_complex_model_name(self) -> None:
        assert codename_to_perm_level('view_my_complex_model') == 1
        assert codename_to_perm_level('delete_my_complex_model') == 4


class CodenameListToPermLevelTestCase(BaseTestCase):
    def test_empty_list(self) -> None:
        assert codename_list_to_perm_level([]) == 0

    def test_single_codename(self) -> None:
        assert codename_list_to_perm_level(['view_model']) == 1

    def test_multiple_codenames_returns_highest(self) -> None:
        codenames = ['view_model', 'add_model', 'change_model']
        assert codename_list_to_perm_level(codenames) == 3

    def test_all_permissions(self) -> None:
        codenames = ['view_model', 'add_model', 'change_model', 'delete_model']
        assert codename_list_to_perm_level(codenames) == 4

    def test_unordered_codenames(self) -> None:
        codenames = ['delete_model', 'view_model', 'add_model']
        assert codename_list_to_perm_level(codenames) == 4

    def test_duplicate_codenames(self) -> None:
        codenames = ['view_model', 'view_model', 'view_model']
        assert codename_list_to_perm_level(codenames) == 1

    def test_mixed_valid_invalid(self) -> None:
        codenames = ['view_model', 'invalid_model', 'delete_model']
        assert codename_list_to_perm_level(codenames) == 4


class PermLevelToIntTestCase(BaseTestCase):
    def test_integer_zero(self) -> None:
        assert perm_level_to_int(0) == 0

    def test_integer_valid_range(self) -> None:
        for i in range(5):
            assert perm_level_to_int(i) == i

    def test_integer_out_of_range_high(self) -> None:
        assert perm_level_to_int(5) == 0
        assert perm_level_to_int(100) == 0

    def test_integer_out_of_range_low(self) -> None:
        assert perm_level_to_int(-1) == 0
        assert perm_level_to_int(-100) == 0

    def test_string_none(self) -> None:
        assert perm_level_to_int('none') == 0
        assert perm_level_to_int('None') == 0
        assert perm_level_to_int('NONE') == 0

    def test_string_view(self) -> None:
        assert perm_level_to_int('view') == 1
        assert perm_level_to_int('View') == 1
        assert perm_level_to_int('VIEW') == 1

    def test_string_add(self) -> None:
        assert perm_level_to_int('add') == 2
        assert perm_level_to_int('Add') == 2
        assert perm_level_to_int('ADD') == 2

    def test_string_change(self) -> None:
        assert perm_level_to_int('change') == 3
        assert perm_level_to_int('Change') == 3
        assert perm_level_to_int('CHANGE') == 3

    def test_string_delete(self) -> None:
        assert perm_level_to_int('delete') == 4
        assert perm_level_to_int('Delete') == 4
        assert perm_level_to_int('DELETE') == 4

    def test_invalid_string(self) -> None:
        assert perm_level_to_int('invalid') == 0
        assert perm_level_to_int('') == 0
        assert perm_level_to_int('random') == 0


class PermLevelToStringTestCase(BaseTestCase):
    def test_level_zero(self) -> None:
        assert perm_level_to_string(0) == 'None'

    def test_level_one(self) -> None:
        assert perm_level_to_string(1) == 'View'

    def test_level_two(self) -> None:
        assert perm_level_to_string(2) == 'Add'

    def test_level_three(self) -> None:
        assert perm_level_to_string(3) == 'Change'

    def test_level_four(self) -> None:
        assert perm_level_to_string(4) == 'Delete'

    def test_string_input(self) -> None:
        assert perm_level_to_string('view') == 'View'
        assert perm_level_to_string('delete') == 'Delete'

    def test_invalid_level_returns_none(self) -> None:
        assert perm_level_to_string(5) == 'None'
        assert perm_level_to_string(-1) == 'None'

    def test_all_string_inputs(self) -> None:
        assert perm_level_to_string('none') == 'None'
        assert perm_level_to_string('view') == 'View'
        assert perm_level_to_string('add') == 'Add'
        assert perm_level_to_string('change') == 'Change'
        assert perm_level_to_string('delete') == 'Delete'


class PermLevelToDjangoPermissionTestCase(BaseTestCase):
    def test_view_permission(self) -> None:
        result = perm_level_to_django_permission(1, 'app_label', 'model')
        assert result == 'app_label.view_model'

    def test_add_permission(self) -> None:
        result = perm_level_to_django_permission(2, 'app_label', 'model')
        assert result == 'app_label.add_model'

    def test_change_permission(self) -> None:
        result = perm_level_to_django_permission(3, 'app_label', 'model')
        assert result == 'app_label.change_model'

    def test_delete_permission(self) -> None:
        result = perm_level_to_django_permission(4, 'app_label', 'model')
        assert result == 'app_label.delete_model'

    def test_none_permission(self) -> None:
        result = perm_level_to_django_permission(0, 'app_label', 'model')
        assert result == 'app_label.none_model'

    def test_complex_app_label(self) -> None:
        result = perm_level_to_django_permission(1, 'my_app_label', 'model')
        assert result == 'my_app_label.view_model'

    def test_complex_model_name(self) -> None:
        result = perm_level_to_django_permission(1, 'app', 'my_model_name')
        assert result == 'app.view_my_model_name'


class HasAppPermissionTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser')

    def test_user_without_permission(self) -> None:
        result = has_app_permission(self.user, 'app_label', 'model', 'view')
        assert result is False

    def test_superuser_has_permission(self) -> None:
        superuser = create_super_user()
        result = has_app_permission(superuser, 'any_app', 'any_model', 'delete')
        assert result is True

    def test_various_actions(self) -> None:
        for action in ['view', 'add', 'change', 'delete']:
            result = has_app_permission(self.user, 'app', 'model', action)
            assert result is False


class HasAppPermissionOr404TestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser')

    def test_raises_permission_error(self) -> None:
        with pytest.raises(PermissionError):
            has_app_permission_or_404(self.user, 'app', 'model', 'view')

    def test_superuser_returns_true(self) -> None:
        superuser = create_super_user()
        result = has_app_permission_or_404(superuser, 'any_app', 'any_model', 'delete')
        assert result is True
