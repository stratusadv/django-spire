from django.contrib.auth.models import Group, User
from django.test import TestCase

from django_spire.auth.mfa.models import MfaCode
from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.service.tests.services import TestUserModelService, TestMfaCodeModelService


class TestInstanceService(TestCase):
    def setUp(self):
        User.services = TestUserModelService()
        MfaCode.services = TestMfaCodeModelService()

        self.user = create_super_user()
        self.group = Group.objects.create(name='Boberts Minions')

    def tearDown(self):
        User.services = None
        MfaCode.services = None

    def test_valid_update_model_fields(self):
        data = {
            'first_name': 'John',
            'last_name': 'Smith'
        }

        created = self.user.services.model_obj_validate_field_data_and_save(**data)
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Smith')
        self.assertFalse(created)

    def test_valid_create_model_fields(self):
        new_user = User()

        data = {
            'first_name': 'John',
            'last_name': 'Smith'
        }

        created = new_user.services.model_obj_validate_field_data_and_save(**data)
        self.assertEqual(new_user.first_name, 'John')
        self.assertEqual(new_user.last_name, 'Smith')
        self.assertIsNotNone(self.user.id)
        self.assertTrue(created)

    def test_invalid_field_name(self):
        # Skips the field and saves the instance.
        data = {
            'invalid_field': 'test'
        }
        created = self.user.services.model_obj_validate_field_data_and_save(**data)
        self.assertFalse(created)

    def test_foreign_key_id_aliases(self):
        mfa = MfaCode.objects.create(
            user=self.user,
            code='123456',
            expiration_datetime='2023-01-01'
        )
        new_user = create_super_user()

        data = {
            'user_id': new_user.id,
        }

        created = mfa.services.model_obj_validate_field_data_and_save(**data)
        self.assertEqual(mfa.user_id, new_user.id)
        self.assertFalse(created)

    def test_obj_foreign_key_id_aliases(self):
        mfa = MfaCode.objects.create(
            user=self.user,
            code='123456',
            expiration_datetime='2023-01-01'
        )
        new_user = create_super_user()

        data = {
            'user': new_user,
        }

        created = mfa.services.model_obj_validate_field_data_and_save(**data)
        self.assertEqual(mfa.user_id, new_user.id)
        self.assertFalse(created)
