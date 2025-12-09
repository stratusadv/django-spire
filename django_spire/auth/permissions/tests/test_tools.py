from __future__ import annotations

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.permissions.permissions import GroupPermissions, ModelPermission
from django_spire.auth.permissions.tools import (
    generate_group_perm_data,
    generate_model_key_permission_map,
    generate_model_permissions,
    generate_special_role_data,
    generate_user_perm_data,
)
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class GenerateModelPermissionsTestCase(BaseTestCase):
    def test_returns_list(self) -> None:
        result = generate_model_permissions()
        assert isinstance(result, list)

    def test_contains_model_permission_instances(self) -> None:
        result = generate_model_permissions()
        for item in result:
            assert isinstance(item, ModelPermission)

    def test_contains_group_permission(self) -> None:
        result = generate_model_permissions()
        names = [mp.name for mp in result]
        assert 'group' in names

    def test_contains_user_permission(self) -> None:
        result = generate_model_permissions()
        names = [mp.name for mp in result]
        assert 'user' in names

    def test_all_have_required_attributes(self) -> None:
        result = generate_model_permissions()
        for mp in result:
            assert hasattr(mp, 'name')
            assert hasattr(mp, 'model_class_path')
            assert hasattr(mp, 'is_proxy_model')

    def test_model_class_path_is_string(self) -> None:
        result = generate_model_permissions()
        for mp in result:
            assert isinstance(mp.model_class_path, str)

    def test_name_is_string(self) -> None:
        result = generate_model_permissions()
        for mp in result:
            assert isinstance(mp.name, str)

    def test_is_proxy_model_is_bool(self) -> None:
        result = generate_model_permissions()
        for mp in result:
            assert isinstance(mp.is_proxy_model, bool)

    def test_result_not_empty(self) -> None:
        result = generate_model_permissions()
        assert len(result) > 0

    def test_result_is_consistent(self) -> None:
        result1 = generate_model_permissions()
        result2 = generate_model_permissions()
        names1 = sorted([mp.name for mp in result1])
        names2 = sorted([mp.name for mp in result2])
        assert names1 == names2


class GenerateModelKeyPermissionMapTestCase(BaseTestCase):
    def test_returns_dict(self) -> None:
        result = generate_model_key_permission_map()
        assert isinstance(result, dict)

    def test_keys_are_lowercase(self) -> None:
        result = generate_model_key_permission_map()
        for key in result:
            assert key == key.lower()

    def test_contains_group_key(self) -> None:
        result = generate_model_key_permission_map()
        assert 'group' in result

    def test_contains_user_key(self) -> None:
        result = generate_model_key_permission_map()
        assert 'user' in result

    def test_values_are_model_permissions(self) -> None:
        result = generate_model_key_permission_map()
        for value in result.values():
            assert isinstance(value, ModelPermission)

    def test_keys_match_permission_names(self) -> None:
        result = generate_model_key_permission_map()
        for key, value in result.items():
            assert key == value.name.lower()

    def test_result_not_empty(self) -> None:
        result = generate_model_key_permission_map()
        assert len(result) > 0

    def test_keys_are_strings(self) -> None:
        result = generate_model_key_permission_map()
        for key in result.keys():
            assert isinstance(key, str)


class GenerateUserPermDataTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser')

    def test_returns_list(self) -> None:
        result = generate_user_perm_data(self.user)
        assert isinstance(result, list)

    def test_contains_app_name_and_level(self) -> None:
        result = generate_user_perm_data(self.user)
        for item in result:
            assert 'app_name' in item
            assert 'level_verbose' in item

    def test_default_level_is_none(self) -> None:
        result = generate_user_perm_data(self.user)
        for item in result:
            assert item['level_verbose'] == 'None'

    def test_user_with_permissions(self) -> None:
        group = AuthGroup.objects.create(name='Test Group')
        self.user.groups.add(group)
        model_permission = ModelPermission(
            name='group',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )
        group_perms = GroupPermissions(group, model_permission)
        group_perms.update_perms(3)

        result = generate_user_perm_data(self.user)
        group_perm = next((p for p in result if p['app_name'] == 'Group'), None)
        assert group_perm is not None
        assert group_perm['level_verbose'] == 'Change'

    def test_returns_data_for_all_registered_permissions(self) -> None:
        result = generate_user_perm_data(self.user)
        model_permissions = generate_model_permissions()
        assert len(result) == len(model_permissions)

    def test_app_name_is_capitalized(self) -> None:
        result = generate_user_perm_data(self.user)
        for item in result:
            assert item['app_name'][0].isupper()

    def test_level_verbose_is_string(self) -> None:
        result = generate_user_perm_data(self.user)
        for item in result:
            assert isinstance(item['level_verbose'], str)

    def test_result_items_are_dicts(self) -> None:
        result = generate_user_perm_data(self.user)
        for item in result:
            assert isinstance(item, dict)

    def test_user_with_delete_permission(self) -> None:
        group = AuthGroup.objects.create(name='Delete Group')
        self.user.groups.add(group)
        model_permission = ModelPermission(
            name='group',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )
        group_perms = GroupPermissions(group, model_permission)
        group_perms.update_perms(4)

        result = generate_user_perm_data(self.user)
        group_perm = next((p for p in result if p['app_name'] == 'Group'), None)
        assert group_perm is not None
        assert group_perm['level_verbose'] == 'Delete'


class GenerateGroupPermDataTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group = AuthGroup.objects.create(name='Test Group')

    def test_returns_list(self) -> None:
        result = generate_group_perm_data(self.group)
        assert isinstance(result, list)

    def test_contains_required_keys(self) -> None:
        result = generate_group_perm_data(self.group)
        for item in result:
            assert 'app_name' in item
            assert 'verbose_app_name' in item
            assert 'level_verbose' in item

    def test_without_special_role(self) -> None:
        result = generate_group_perm_data(self.group, with_special_role=False)
        for item in result:
            assert 'special_role_data' not in item

    def test_with_special_role(self) -> None:
        result = generate_group_perm_data(self.group, with_special_role=True)
        for item in result:
            assert 'special_role_data' in item

    def test_default_level_is_none(self) -> None:
        result = generate_group_perm_data(self.group)
        for item in result:
            assert item['level_verbose'] == 'None'

    def test_group_with_permissions(self) -> None:
        model_permission = ModelPermission(
            name='group',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )
        group_perms = GroupPermissions(self.group, model_permission)
        group_perms.update_perms(4)

        result = generate_group_perm_data(self.group)
        group_perm = next((p for p in result if p['app_name'] == 'Group'), None)
        assert group_perm is not None
        assert group_perm['level_verbose'] == 'Delete'

    def test_app_name_is_capitalized(self) -> None:
        result = generate_group_perm_data(self.group)
        for item in result:
            assert item['app_name'][0].isupper()

    def test_result_items_are_dicts(self) -> None:
        result = generate_group_perm_data(self.group)
        for item in result:
            assert isinstance(item, dict)

    def test_level_verbose_is_string(self) -> None:
        result = generate_group_perm_data(self.group)
        for item in result:
            assert isinstance(item['level_verbose'], str)

    def test_returns_data_for_all_registered_permissions(self) -> None:
        result = generate_group_perm_data(self.group)
        model_permissions = generate_model_permissions()
        assert len(result) == len(model_permissions)

    def test_special_role_data_is_list(self) -> None:
        result = generate_group_perm_data(self.group, with_special_role=True)
        for item in result:
            assert isinstance(item['special_role_data'], list)


class GenerateSpecialRoleDataTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group = AuthGroup.objects.create(name='Test Group')
        self.model_permission = ModelPermission(
            name='group',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )
        self.group_permissions = GroupPermissions(self.group, self.model_permission)

    def test_returns_list(self) -> None:
        result = generate_special_role_data(self.group_permissions)
        assert isinstance(result, list)

    def test_special_role_dict_structure(self) -> None:
        result = generate_special_role_data(self.group_permissions)
        for item in result:
            assert 'name' in item
            assert 'codename' in item
            assert 'has_access' in item

    def test_has_access_default_false(self) -> None:
        result = generate_special_role_data(self.group_permissions)
        for item in result:
            assert item['has_access'] is False

    def test_codename_starts_with_can(self) -> None:
        result = generate_special_role_data(self.group_permissions)
        for item in result:
            assert item['codename'].startswith('can')

    def test_name_is_string(self) -> None:
        result = generate_special_role_data(self.group_permissions)
        for item in result:
            assert isinstance(item['name'], str)

    def test_codename_is_string(self) -> None:
        result = generate_special_role_data(self.group_permissions)
        for item in result:
            assert isinstance(item['codename'], str)

    def test_has_access_is_bool(self) -> None:
        result = generate_special_role_data(self.group_permissions)
        for item in result:
            assert isinstance(item['has_access'], bool)

    def test_result_items_are_dicts(self) -> None:
        result = generate_special_role_data(self.group_permissions)
        for item in result:
            assert isinstance(item, dict)
