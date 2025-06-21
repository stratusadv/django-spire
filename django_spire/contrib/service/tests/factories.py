from django_spire.auth.user.models import User
from django_spire.contrib.service.tests.services import TestUserService


class TestFakeUserModel(User):
    services = TestUserService()

    class Meta:
        app_label = 'auth'
        proxy = True
        managed = False
