from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.auth.group.models import AuthGroup
    from django_spire.auth.user.models import AuthUser


class AuthUserService(BaseDjangoModelService['AuthUser']):
    obj: AuthUser

    def get_user_choices(self) -> list[tuple[int, str]]:
        users = self.obj_class.objects.filter(is_active=True)
        return [[user.id, user.get_full_name()] for user in users]

    def get_user_choices_by_group(self, group: AuthGroup) -> list[tuple[int, str]]:
        users = self.obj_class.objects.filter(is_active=True, groups=group)
        return [[user.id, user.get_full_name()] for user in users]
