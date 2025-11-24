from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import Permission, Group, User
from django.contrib.contenttypes.models import ContentType

from django_spire.auth.group.utils import (
    codename_list_to_perm_level,
    codename_to_perm_level,
    perm_level_to_string
)
from django_spire.auth.permissions.consts import VALID_PERMISSION_LEVELS
from django_spire.core.utils import get_object_from_module_string

if TYPE_CHECKING:
    from django.db.models import QuerySet, Model


class ModelPermission:
    def __init__(
            self,
            name: str,
            model_class_path: str,
            is_proxy_model: bool,
            verbose_name: str | None = None,
    ):
        self.name = name
        self.model_class_path = model_class_path
        self.is_proxy_model = is_proxy_model
        self.verbose_name = verbose_name

    @property
    def model_class(self) -> type[Model]:
        return get_object_from_module_string(self.model_class_path)



class ModelPermissions:
    def __init__(self, model_permission: ModelPermission):
        self.model = model_permission.model_class
        self.is_proxy_model = model_permission.is_proxy_model

        # All the permissions accessible to this model
        self.permissions: QuerySet[Permission] = self._set_model_perms()

    @property
    def app_label(self) -> str:
        # Used to generate codenames. For example delete_app_label
        return self.model._meta.app_label

    @property
    def model_name(self) -> str:
        return self.model._meta.model_name

    def find_permissions_by_level(
        self,
        perm_level: VALID_PERMISSION_LEVELS | None
    ) -> list[Permission]:
        permission_list = []

        for perm in self.permissions:
            if codename_to_perm_level(perm.codename) <= perm_level:
                permission_list.append(perm)

        return permission_list

    def get_special_role(self, codename: str) -> Permission | None:
        for perm in self.permissions:
            if perm.codename == codename:
                return perm

        return None

    def _set_model_perms(self) -> QuerySet[Permission]:
        content_type = ContentType.objects.get_for_model(
            self.model(),
            for_concrete_model=not self.is_proxy_model
        )

        return Permission.objects.filter(content_type=content_type)

    def special_role_list(self) -> list[Permission]:
        return [
            perm
            for perm in self.permissions
            if perm.codename.startswith('can')
        ]


class GroupPermissions:
    def __init__(self, group: Group, model_permission: ModelPermission):
        """
            Helper to use Django Groups as a cascading permission structure.
        """
        self.group = group
        self.model_permissions = ModelPermissions(model_permission)
        self.group_perms = self.group.permissions.all()

    def add_special_role(self, codename: str) -> None:
        special_role = self.model_permissions.get_special_role(codename)

        if special_role is not None:
            self.group.permissions.add(special_role)
            self.set_group_perms()

    def has_special_role(self, codename: str) -> bool:
        for perm in self.group_perms:
            if perm.codename == codename:
                return True

        return False

    def perm_level(self) -> VALID_PERMISSION_LEVELS:
        codename_list = []

        for perm in self.group_perms:
            if perm.codename.split('_')[-1] == self.model_permissions.model_name:
                codename_list.append(perm.codename)

        return codename_list_to_perm_level(codename_list)

    def perm_level_verbose(self) -> str:
        return perm_level_to_string(self.perm_level())

    @staticmethod
    def remove_special_permissions(perm_list: list | QuerySet) -> list:
        return [
            perm for perm in perm_list if not perm.codename.startswith('can')
        ]

    def update_perms(self, perm_level: VALID_PERMISSION_LEVELS) -> None:
        cascading_perms = self.remove_special_permissions(
            self.model_permissions.find_permissions_by_level(perm_level)
        )

        cascading_perms_queryset = Permission.objects.filter(
            pk__in=[perm.pk for perm in cascading_perms]
        )
        self.group.permissions.add(*cascading_perms_queryset)

        cascading_perms_id_list = [perm.pk for perm in cascading_perms]
        prohibited_permissions = self.remove_special_permissions(
            self.model_permissions.permissions.exclude(
                id__in=cascading_perms_id_list
            )
        )

        self.group.permissions.remove(*prohibited_permissions)

        self.set_group_perms()

    def remove_special_role(self, codename: str) -> None:
        special_role = self.model_permissions.get_special_role(codename)

        if special_role:
            self.group.permissions.remove(special_role)
            self.set_group_perms()

    def set_group_perms(self) -> None:
        self.group_perms = self.group.permissions.all()

    def toggle_special_role(self, codename: str) -> None:
        if self.has_special_role(codename):
            self.remove_special_role(codename)
        else:
            self.add_special_role(codename)


class UserPermissionHelper:
    def __init__(self, user: User, model_permission: ModelPermission):
        """
            Helper to query user's current cascading permissions
        """
        self.user = user
        self.model_permissions = ModelPermissions(model_permission)
        self.user_perms = self.get_user_perms()

    def get_user_perms(self) -> QuerySet[Permission]:
        return Permission.objects.filter(group__user=self.user).distinct()

    def perm_level(self) -> VALID_PERMISSION_LEVELS:
        codename_list = []

        for perm in self.user_perms:
            if perm.codename.split('_')[-1] == self.model_permissions.model_name:
                codename_list.append(perm.codename)

        return codename_list_to_perm_level(codename_list)

    def perm_level_verbose(self) -> str:
        return perm_level_to_string(self.perm_level())
