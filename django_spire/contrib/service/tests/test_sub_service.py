from django.contrib.auth.models import Group, User
from django.test import TestCase

from django_spire.auth.mfa.models import MfaCode
from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.service.tests.services import TestUserModelService, TestMfaCodeModelService


class TestSubService(TestCase):
    def setUp(self):
        User.services = TestUserModelService()
        MfaCode.services = TestMfaCodeModelService()

        self.user = create_super_user()
        self.group = Group.objects.create(name='Boberts Minions')

    def tearDown(self):
        User.services = None
        MfaCode.services = None

    def test_sub_service_access(self):
        data = {
            'first_name': 'John',
            'last_name': 'Smith'
        }

        created = self.user.services.model_obj_validate_field_data_and_save(**data)

        self.assertEqual(self.user.services.sub.get_the_full_name(), 'John Smith')

