from __future__ import annotations

from typing import TYPE_CHECKING


from django_spire.contrib.service.django_model_service import BaseDjangoModelService

# Simulates imports as real environment.
if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django_spire.auth.mfa.models import MfaCode


class TestUserSubService(BaseDjangoModelService):
    user: User

    def full_name(self):
        return self.user.get_full_name()


class TestUserService(BaseDjangoModelService):
    user: User
    sub: TestUserService = TestUserSubService

    def get_the_first_name(self, weather: str = ''):
        return self.user.first_name + weather

    def set_inactive(self):
        self.user.is_active = False
        self.user.save()


class TestMfaCodeService(BaseDjangoModelService):
    mfa_code: MfaCode

    def get_code_length(self):
        return len(self.mfa_code.code)

