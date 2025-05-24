from django.contrib.auth.models import Group
from django.core.exceptions import FieldDoesNotExist
from django.test import TestCase

from django_spire.auth.mfa.models import MfaCode
from django_spire.auth.user.tests.factories import create_super_user
from django_spire.contrib.services.update_service import update_model_fields


class UpdateServiceTestCase(TestCase):
    def setUp(self):
        self.user = create_super_user()
        self.group = Group.objects.create(name='Bobberts Minions')

    def test_valid_update_model_fields(self):
        data = {
            'first_name': 'John',
            'last_name': 'Smith'
        }

        user = update_model_fields(self.user, **data)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Smith')

    def test_invalid_field_name(self):
        data = {
            'invalid_field': 'test'
        }

        with self.assertRaises(FieldDoesNotExist):
            update_model_fields(self.user, **data)

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
        mfa = update_model_fields(mfa, **data)
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
        mfa = update_model_fields(mfa, **data)
        self.assertEqual(mfa.user_id, new_user.id)
