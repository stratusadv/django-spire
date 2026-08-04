from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.auth.group.models import AuthGroup
    from django_spire.auth.user.models import AuthUser


class AuthUserService(BaseDjangoModelService['AuthUser']):
    obj: AuthUser

    def save_model_obj(
        self,
        user: AuthUser,
        email: str,
        **field_data: dict
    ) -> AuthUser:

        obj, created = super().save_model_obj(
            email=email,
            username=email,
            **field_data
        )
        verb = 'created' if created else 'updated'

        obj.add_activity(
            user=user, verb=verb, information=f'{user.get_full_name()} {verb} user {obj.username}.'
        )

        return obj

    def get_user_choices(self) -> list[list]:
        users = self.obj_class.objects.filter(is_active=True)
        return [[user.id, user.get_full_name()] for user in users]

    def get_user_choices_by_group(self, group: AuthGroup) -> list[list]:
        users = self.obj_class.objects.filter(is_active=True, groups=group)
        return [[user.id, user.get_full_name()] for user in users]
