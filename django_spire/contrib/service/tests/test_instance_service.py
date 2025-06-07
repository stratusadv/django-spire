from django.contrib.auth.models import Group, User
from django.test import TestCase

from django_spire.auth.mfa.models import MfaCode
from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.service.tests.services import UserModelService, MfaCodeModelService


class UpdateServiceTestCase(TestCase):
    def setUp(self):
        User.services = UserModelService()
        MfaCode.services = MfaCodeModelService()
        self.user = create_super_user()
        self.group = Group.objects.create(name='Boberts Minions')
        # self.user_service = UserModelService()

    def tearDown(self):
        User.services = None
        MfaCode.services = None

    def test_valid_update_model_fields(self):
        data = {
            'first_name': 'John',
            'last_name': 'Smith'
        }

        user, created = self.user.services.save_instance(**data)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Smith')

    def test_valid_create_model_fields(self):
        data = {
            'first_name': 'John',
            'last_name': 'Smith'
        }

        user, created = self.user.services.save_instance(**data)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Smith')
        self.assertIsNotNone(user.id)

    def test_invalid_field_name(self):
        # Skips the field and saves the instance.
        data = {
            'invalid_field': 'test'
        }
        self.user.services.save_instance(**data)

    def test_fk_id_aliases(self):
        mfa = MfaCode.objects.create(
            user=self.user,
            code='123456',
            expiration_datetime='2023-01-01'
        )
        new_user = create_super_user()

        data = {
            'user_id': new_user.id,
        }

        mfa, created = mfa.services.save_instance(**data)
        self.assertEqual(mfa.user_id, new_user.id)

    def test_obj_fk_id_aliases(self):
        mfa = MfaCode.objects.create(
            user=self.user,
            code='123456',
            expiration_datetime='2023-01-01'
        )
        new_user = create_super_user()

        data = {
            'user': new_user,
        }

        mfa, created = mfa.services.save_instance(**data)
        self.assertEqual(mfa.user_id, new_user.id)
