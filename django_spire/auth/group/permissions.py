from __future__ import annotations

from typing_extensions import TYPE_CHECKING

from django.contrib.auth.models import Permission, Group, User
from django.contrib.contenttypes.models import ContentType

from django_spire.auth.group.constants import (
    PERMISSION_MODELS_DICT,
    VALID_PERMISSION_LEVELS
)
from django_spire.auth.group.utils import (
    codename_list_to_perm_level,
    codename_to_perm_level,
    perm_level_to_string
)

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from typing_extensions import Any


class ModelPermissions:
    def __init__(self, model_key: str):
        if model_key not in PERMISSION_MODELS_DICT:
            message = f'Model key {model_key} not in permission models dict.'
            raise KeyError(message)

        self.model = PERMISSION_MODELS_DICT[model_key]['model']
        self.is_proxy_model = PERMISSION_MODELS_DICT[model_key]['is_proxy_model']

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
    def __init__(self, group: Group, model_key: str):
        """
            Helper to use Django Groups as a cascading permission structure.
        """
        self.group = group
        self.model_permissions = ModelPermissions(model_key.lower())
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
    def __init__(self, user: User, model_key: str):
        """
            Helper to query user's current cascading permissions
        """
        self.user = user
        self.model_permissions = ModelPermissions(model_key.lower())
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


def generate_user_perm_data(user: User) -> list[dict]:
    perm_data = []

    for key in PERMISSION_MODELS_DICT:
        user_permissions = UserPermissionHelper(user, key)

        perm_data.append({
            'app_name': key.capitalize(),
            'level_verbose': user_permissions.perm_level_verbose()
        })

    return perm_data


def generate_group_perm_data(
    group: Group,
    with_special_role: bool = False
) -> list[dict]:
    from django_spire.auth.group.constants import PERMISSION_MODELS_DICT

    perm_data = []

    for key in PERMISSION_MODELS_DICT:
        group_permissions = GroupPermissions(group=group, model_key=key)

        perm_information_dic = {
            'app_name': key.capitalize(),
            'level_verbose': group_permissions.perm_level_verbose()
        }

        if with_special_role:
            perm_information_dic['special_role_data'] = generate_special_role_data(group_permissions)

        perm_data.append(perm_information_dic)

    return perm_data


def generate_special_role_data(
    group_permissions: GroupPermissions
) -> list[dict[str, Any]]:
    special_role_data = []

    model_permissions = group_permissions.model_permissions

    for special_role in model_permissions.special_role_list():
        special_role_data.append({
            'name': special_role.name,
            'codename': special_role.codename,
            'has_access': group_permissions.has_special_role(special_role.codename)
        })

    return special_role_data
