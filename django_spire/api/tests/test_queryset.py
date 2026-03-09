from django.test import TestCase

from django_spire.api.models import ApiAccess


class ApiAccessQuerySetTestCase(TestCase):
    def setUp(self):
        self.key1 = "key1_123456789"
        self.key2 = "key2_123456789"

        self.access1 = ApiAccess.objects.create(name="Active Access")
        self.access1.set_key_and_save(self.key1)

        self.access2 = ApiAccess.objects.create(name="Inactive Access")
        self.access2.set_key_and_save(self.key2)
        self.access2.set_inactive()

    def test_is_valid_key(self):
        # Valid active key
        self.assertTrue(ApiAccess.objects.is_valid_key(self.key1))

        # Valid but inactive key
        self.assertFalse(ApiAccess.objects.is_valid_key(self.key2))

        # Invalid key
        self.assertFalse(ApiAccess.objects.is_valid_key("wrong_key"))

    def test_get_by_key_or_none(self):
        # Valid active key
        found = ApiAccess.objects.get_by_key_or_none(self.key1)
        self.assertEqual(found, self.access1)

        # Valid but inactive key
        found = ApiAccess.objects.get_by_key_or_none(self.key2)
        self.assertIsNone(found)

        # Invalid key
        found = ApiAccess.objects.get_by_key_or_none("wrong_key")
        self.assertIsNone(found)
