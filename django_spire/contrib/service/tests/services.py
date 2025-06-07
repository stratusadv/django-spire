from django.contrib.auth.models import User

from django_spire.auth.mfa.models import MfaCode
from django_spire.contrib.service.model_service import BaseModelService


class UserSubModelService(BaseModelService):
    user: User

    def get_the_name(self):
        return self.user.get_full_name()


class UserModelService(BaseModelService):
    user: User
    sub: UserSubModelService = UserSubModelService()


class MfaCodeModelService(BaseModelService):
    mfa_code: MfaCode