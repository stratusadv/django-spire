from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django_spire.auth.group.models import AuthGroup
    from django_spire.auth.user.models import AuthUser


class AuthGroupService(BaseDjangoModelService['AuthGroup']):
    obj: AuthGroup

    def save_model_obj(self, user: AuthUser, **field_data: dict) -> AuthGroup:
        obj, created = super().save_model_obj(**field_data)
        verb = 'created' if created else 'updated'

        obj.add_activity(
            user=user, verb=verb, information=f'{user.get_full_name()} {verb} group {obj.name}.'
        )

        return obj
