from __future__ import annotations

import random
import string

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

    def random_reset_password(self) -> str:
        chars = string.ascii_letters + string.digits
        password = [
            random.SystemRandom().choice(string.ascii_lowercase),
            random.SystemRandom().choice(string.ascii_uppercase),
            random.SystemRandom().choice(string.digits),
        ]
        password += [random.SystemRandom().choice(chars) for _ in range(5)]
        random.SystemRandom().shuffle(password)

        password_str = ''.join(password)

        self.obj.set_password(password_str)
        self.obj.save(update_fields=['password'])

        return password_str
