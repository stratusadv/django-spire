from __future__ import annotations

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.permissions.permissions import (
    GroupPermissions,
    ModelPermission,
    ModelPermissions,
    UserPermissionHelper,
)
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


class ModelPermissionTestCase(BaseTestCase):
    def test_model_permission_attributes(self) -> None:
        mp = ModelPermission(
            name='test',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True,
            verbose_name='Test Permission'
        )
        assert mp.name == 'test'
        assert mp.model_class_path == 'django_spire.auth.group.models.AuthGroup'
        assert mp.is_proxy_model
        assert mp.verbose_name == 'Test Permission'

    def test_model_class_property(self) -> None:
        mp = ModelPermission(
            name='group',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )
        assert mp.model_class == AuthGroup

    def test_model_permission_without_verbose_name(self) -> None:
        mp = ModelPermission(
            name='test',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )
        assert mp.verbose_name is None

    def test_model_permission_non_proxy(self) -> None:
        mp = ModelPermission(
            name='test',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=False
        )
        assert not mp.is_proxy_model

    def test_model_permission_name_case_preserved(self) -> None:
        mp = ModelPermission(
            name='TestName',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )
        assert mp.name == 'TestName'

    def test_model_permission_verbose_name_unicode(self) -> None:
        mp = ModelPermission(
            name='test',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True,
            verbose_name='Tëst Përmission'
        )
        assert mp.verbose_name == 'Tëst Përmission'


class ModelPermissionsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.model_permission = ModelPermission(
            name='group',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )
        self.model_permissions = ModelPermissions(self.model_permission)

    def test_app_label(self) -> None:
        assert self.model_permissions.app_label == 'django_spire_auth_group'

    def test_model_name(self) -> None:
        assert self.model_permissions.model_name == 'authgroup'

    def test_permissions_queryset(self) -> None:
        assert self.model_permissions.permissions.count() > 0

    def test_find_permissions_by_level_none(self) -> None:
        perms = self.model_permissions.find_permissions_by_level(0)
        assert len(perms) == 0

    def test_find_permissions_by_level_view(self) -> None:
        perms = self.model_permissions.find_permissions_by_level(1)
        codenames = [p.codename for p in perms]
        assert 'view_authgroup' in codenames

    def test_find_permissions_by_level_add(self) -> None:
        perms = self.model_permissions.find_permissions_by_level(2)
        codenames = [p.codename for p in perms]
        assert 'view_authgroup' in codenames
        assert 'add_authgroup' in codenames

    def test_find_permissions_by_level_change(self) -> None:
        perms = self.model_permissions.find_permissions_by_level(3)
        codenames = [p.codename for p in perms]
        assert 'view_authgroup' in codenames
        assert 'add_authgroup' in codenames
        assert 'change_authgroup' in codenames

    def test_find_permissions_by_level_delete(self) -> None:
        perms = self.model_permissions.find_permissions_by_level(4)
        codenames = [p.codename for p in perms]
        assert 'view_authgroup' in codenames
        assert 'add_authgroup' in codenames
        assert 'change_authgroup' in codenames
        assert 'delete_authgroup' in codenames

    def test_special_role_list(self) -> None:
        roles = self.model_permissions.special_role_list()
        for role in roles:
            assert role.codename.startswith('can')

    def test_get_special_role_not_found(self) -> None:
        result = self.model_permissions.get_special_role('nonexistent_role')
        assert result is None

    def test_permissions_returns_queryset(self) -> None:
        assert hasattr(self.model_permissions.permissions, 'filter')

    def test_model_attribute(self) -> None:
        assert self.model_permissions.model == AuthGroup

    def test_is_proxy_model_attribute(self) -> None:
        assert self.model_permissions.is_proxy_model

    def test_find_permissions_by_level_returns_list(self) -> None:
        perms = self.model_permissions.find_permissions_by_level(2)
        assert isinstance(perms, list)

    def test_special_role_list_returns_list(self) -> None:
        roles = self.model_permissions.special_role_list()
        assert isinstance(roles, list)


class GroupPermissionsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.group = AuthGroup.objects.create(name='Test Group')
        self.model_permission = ModelPermission(
            name='group',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )
        self.group_permissions = GroupPermissions(self.group, self.model_permission)

    def test_initial_perm_level_is_zero(self) -> None:
        assert self.group_permissions.perm_level() == 0

    def test_perm_level_verbose_none(self) -> None:
        assert self.group_permissions.perm_level_verbose() == 'None'

    def test_update_perms_to_view(self) -> None:
        self.group_permissions.update_perms(1)
        assert self.group_permissions.perm_level() == 1
        assert self.group_permissions.perm_level_verbose() == 'View'

    def test_update_perms_to_add(self) -> None:
        self.group_permissions.update_perms(2)
        assert self.group_permissions.perm_level() == 2
        assert self.group_permissions.perm_level_verbose() == 'Add'

    def test_update_perms_to_change(self) -> None:
        self.group_permissions.update_perms(3)
        assert self.group_permissions.perm_level() == 3
        assert self.group_permissions.perm_level_verbose() == 'Change'

    def test_update_perms_to_delete(self) -> None:
        self.group_permissions.update_perms(4)
        assert self.group_permissions.perm_level() == 4
        assert self.group_permissions.perm_level_verbose() == 'Delete'

    def test_update_perms_downgrades(self) -> None:
        self.group_permissions.update_perms(4)
        self.group_permissions.update_perms(1)
        assert self.group_permissions.perm_level() == 1

    def test_update_perms_to_none(self) -> None:
        self.group_permissions.update_perms(4)
        self.group_permissions.update_perms(0)
        assert self.group_permissions.perm_level() == 0

    def test_remove_special_permissions(self) -> None:
        content_type = ContentType.objects.get_for_model(AuthGroup)
        perms = Permission.objects.filter(content_type=content_type)
        filtered = GroupPermissions.remove_special_permissions(perms)
        for perm in filtered:
            assert not perm.codename.startswith('can')

    def test_set_group_perms_updates(self) -> None:
        self.group_permissions.update_perms(2)
        self.group_permissions.set_group_perms()
        assert self.group_permissions.perm_level() == 2

    def test_has_special_role_false(self) -> None:
        assert not self.group_permissions.has_special_role('nonexistent')

    def test_group_attribute(self) -> None:
        assert self.group_permissions.group == self.group

    def test_model_permissions_attribute(self) -> None:
        assert self.group_permissions.model_permissions is not None

    def test_group_perms_attribute(self) -> None:
        assert self.group_permissions.group_perms is not None

    def test_update_perms_multiple_times(self) -> None:
        for level in [1, 2, 3, 4, 3, 2, 1, 0]:
            self.group_permissions.update_perms(level)
            assert self.group_permissions.perm_level() == level

    def test_perm_level_returns_int(self) -> None:
        level = self.group_permissions.perm_level()
        assert isinstance(level, int)

    def test_perm_level_verbose_returns_str(self) -> None:
        verbose = self.group_permissions.perm_level_verbose()
        assert isinstance(verbose, str)

    def test_remove_special_permissions_with_list(self) -> None:
        content_type = ContentType.objects.get_for_model(AuthGroup)
        perms = list(Permission.objects.filter(content_type=content_type))
        filtered = GroupPermissions.remove_special_permissions(perms)
        assert isinstance(filtered, list)


class UserPermissionHelperTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user = create_user(username='testuser')
        self.group = AuthGroup.objects.create(name='Test Group')
        self.model_permission = ModelPermission(
            name='group',
            model_class_path='django_spire.auth.group.models.AuthGroup',
            is_proxy_model=True
        )

    def test_initial_perm_level_is_zero(self) -> None:
        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.perm_level() == 0

    def test_perm_level_verbose_none(self) -> None:
        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.perm_level_verbose() == 'None'

    def test_user_inherits_group_permissions(self) -> None:
        self.user.groups.add(self.group)
        group_perms = GroupPermissions(self.group, self.model_permission)
        group_perms.update_perms(3)

        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.perm_level() == 3
        assert helper.perm_level_verbose() == 'Change'

    def test_user_inherits_highest_permission(self) -> None:
        group2 = AuthGroup.objects.create(name='Group 2')
        self.user.groups.add(self.group, group2)

        group_perms1 = GroupPermissions(self.group, self.model_permission)
        group_perms1.update_perms(1)

        group_perms2 = GroupPermissions(group2, self.model_permission)
        group_perms2.update_perms(4)

        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.perm_level() == 4

    def test_user_no_groups_no_permissions(self) -> None:
        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.perm_level() == 0

    def test_get_user_perms_returns_queryset(self) -> None:
        helper = UserPermissionHelper(self.user, self.model_permission)
        perms = helper.get_user_perms()
        assert perms is not None

    def test_user_attribute(self) -> None:
        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.user == self.user

    def test_model_permissions_attribute(self) -> None:
        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.model_permissions is not None

    def test_user_perms_attribute(self) -> None:
        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.user_perms is not None

    def test_perm_level_returns_int(self) -> None:
        helper = UserPermissionHelper(self.user, self.model_permission)
        level = helper.perm_level()
        assert isinstance(level, int)

    def test_perm_level_verbose_returns_str(self) -> None:
        helper = UserPermissionHelper(self.user, self.model_permission)
        verbose = helper.perm_level_verbose()
        assert isinstance(verbose, str)

    def test_user_removed_from_group_loses_permissions(self) -> None:
        self.user.groups.add(self.group)
        group_perms = GroupPermissions(self.group, self.model_permission)
        group_perms.update_perms(3)

        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.perm_level() == 3

        self.user.groups.remove(self.group)
        helper2 = UserPermissionHelper(self.user, self.model_permission)
        assert helper2.perm_level() == 0

    def test_multiple_groups_same_permission_level(self) -> None:
        group2 = AuthGroup.objects.create(name='Group 2')
        self.user.groups.add(self.group, group2)

        group_perms1 = GroupPermissions(self.group, self.model_permission)
        group_perms1.update_perms(2)

        group_perms2 = GroupPermissions(group2, self.model_permission)
        group_perms2.update_perms(2)

        helper = UserPermissionHelper(self.user, self.model_permission)
        assert helper.perm_level() == 2
