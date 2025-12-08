from __future__ import annotations

from typing import TYPE_CHECKING

from django.apps import apps

from django_spire.auth.permissions.permissions import (
    GroupPermissions,
    ModelPermission,
    UserPermissionHelper
)

if TYPE_CHECKING:
    from typing import Any

    from django.contrib.auth.models import User, Group


def generate_model_permissions() -> list[ModelPermission]:
    model_permissions = []

    for app_config in apps.get_app_configs():
        if hasattr(app_config, 'MODEL_PERMISSIONS'):
            for model_permission in app_config.MODEL_PERMISSIONS:
                model_permissions.append(
                    ModelPermission(**model_permission)
                )

    return model_permissions

def generate_model_key_permission_map() -> dict[str, ModelPermission]:
    return {
        model_permission.name.lower(): model_permission
        for model_permission in generate_model_permissions()
    }

def generate_user_perm_data(user: User) -> list[dict]:
    perm_data = []

    for permission in generate_model_permissions():

        user_permissions = UserPermissionHelper(user, permission)

        perm_data.append({
            'app_name': permission.name.capitalize(),
            'level_verbose': user_permissions.perm_level_verbose()
        })

    return perm_data


def generate_group_perm_data(
        group: Group,
        with_special_role: bool = False
) -> list[dict]:

    perm_data = []

    for model_permission in generate_model_permissions():
        group_permissions = GroupPermissions(group=group, model_permission=model_permission)

        perm_information_dic = {
            'app_name': model_permission.name.capitalize(),
            'verbose_app_name': model_permission.verbose_name,
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
