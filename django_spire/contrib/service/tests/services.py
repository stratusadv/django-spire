from django.contrib.auth.models import User

from django_spire.auth.mfa.models import MfaCode
from django_spire.contrib.service.django_model_service import BaseDjangoModelService


class TestUserSubModelService(BaseDjangoModelService):
    user: User

    def get_the_full_name(self):
        return self.user.get_full_name()


class TestUserModelService(BaseDjangoModelService):
    user: User
    sub: TestUserSubModelService = TestUserSubModelService()

    def get_the_first_name(self, weather: str = ''):
        return self.user.first_name + weather


class TestMfaCodeModelService(BaseDjangoModelService):
    mfa_code: MfaCode

    def get_code_length(self):
        return len(self.mfa_code.code)