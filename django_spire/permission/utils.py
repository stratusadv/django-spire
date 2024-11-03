from __future__ import annotations

from typing_extensions import Union

from django.contrib.auth.models import Group, User

from django_spire.permission.constants import (
    PERMISSIONS_LEVEL_CHOICES,
    VALID_PERMISSION_LEVELS
)


def add_users_to_group(group: Group, user_list: list[User]):
    for user in user_list:
        user.groups.add(group)


def codename_to_perm_level(codename: str) -> int:
    return perm_level_to_int(codename.split('_')[0])


def codename_list_to_perm_level(codenames_list: list[str]) -> int:
    perm_level = 0
    for codename in codenames_list:
        temp_perm_level = perm_level_to_int(codename.split('_')[0])
        if temp_perm_level > perm_level:
            perm_level = temp_perm_level
    return perm_level


def perm_level_to_int(perm_level: Union[VALID_PERMISSION_LEVELS, str]) -> int:
    if isinstance(perm_level, int) and 4 >= perm_level >= 0:
        return perm_level
    elif isinstance(perm_level, str):
        for perm in PERMISSIONS_LEVEL_CHOICES:
            if perm_level.lower() == perm[1].lower():
                return perm[0]
    return 0


def perm_level_to_string(perm_level: Union[VALID_PERMISSION_LEVELS, str]) -> str:
    perm_level = perm_level_to_int(perm_level)
    for perm in PERMISSIONS_LEVEL_CHOICES:
        if perm_level == perm[0]:
            return perm[1].capitalize()
    return 'None'


def perm_level_to_django_permission(
        perm_level: VALID_PERMISSION_LEVELS,
        app_label: str,
        model_name: str
) -> str:
    perm_level = dict(PERMISSIONS_LEVEL_CHOICES)[perm_level_to_int(perm_level)]
    return f'{app_label}.{perm_level.lower()}_{model_name}'


def has_app_permission(user: User, app_label: str, model_name: str, action: str) -> bool:
    return user.has_perm(f'{app_label}.{action}_{model_name}')


def has_app_permission_or_404(user: User, app_label: str, model_name: str, action: str) -> bool:
    if not has_app_permission(user, app_label, model_name, action):
        raise PermissionError

    return True
