from django.contrib.auth.models import User

from django_spire.auth.mfa.models import MfaCode
from django_spire.contrib.service.model_service import BaseModelService


class TestUserSubModelService(BaseModelService):
    user: User

    def get_the_full_name(self):
        return self.user.get_full_name()


class TestUserModelService(BaseModelService):
    user: User
    sub: TestUserSubModelService = TestUserSubModelService()

    def get_the_first_name(self):
        return self.user.first_name


class TestMfaCodeModelService(BaseModelService):
    mfa_code: MfaCode

    def get_code_length(self):
        return len(self.mfa_code.code)