from django.test import TestCase

from django_spire.api.choices import ApiAccessLevelChoices
from django_spire.api.models import ApiAccess
from django_spire.api.tools import hash_string


class ApiAccessModelTestCase(TestCase):
    def setUp(self):
        self.raw_key = "test_api_key_123456789"
        self.api_access = ApiAccess.objects.create(name="Test API")
        self.api_access.set_key_and_save(self.raw_key)

    def test_set_key_and_save(self):
        self.assertEqual(self.api_access.hashed_key, hash_string(self.raw_key))

        expected_hint = "test ... 6789"
        self.assertEqual(self.api_access.key_hint, expected_hint)

    def test_str_method(self):
        expected_str = f"Test API - test ... 6789"
        self.assertEqual(str(self.api_access), expected_str)

    def test_default_level(self):
        self.assertEqual(self.api_access.level, ApiAccessLevelChoices.VIEW)
