from django.contrib.auth.models import User
from django.test import TestCase

from django_spire.auth.mfa.models import MfaCode
from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.service import BaseDjangoModelService
from django_spire.contrib.service.exceptions import ServiceException
from django_spire.contrib.service.tests.services import TestUserService, TestUserSubService


class TestBaseService(TestCase):
    def setUp(self):

        self.user = create_super_user()
        self.service = TestUserService(self.user)
        self.user.service = self.service

    def test_initialization(self):
        print(self.user.service.get_the_first_name('bad'))


    # def test_error_no_non_base_service(self):
    #     with self.assertRaises(ServiceException):
    #         class ErrorTestUserService(BaseDjangoModelService):
    #             sub: TestUserService = TestUserSubService()
    #
    # def test_error_more_than_one_non_base_service(self):
    #
    #     with self.assertRaises(ServiceException):
    #         class ErrorTestUserService(BaseDjangoModelService):
    #             user: User
    #             mfa: MfaCode
    #             sub: TestUserService = TestUserSubService()
