from django.test import TestCase

from django_spire.api.models import ApiAccess


class ApiAccessQuerySetTestCase(TestCase):
    def setUp(self) -> None:
        self.key1 = "key1_123456789"
        self.key2 = "key2_123456789"

        self.access1 = ApiAccess.objects.create(name="Active Access")
        self.access1.set_key_and_save(self.key1)

        self.access2 = ApiAccess.objects.create(name="Inactive Access")
        self.access2.set_key_and_save(self.key2)
        self.access2.set_inactive()

    def test_is_valid_key(self) -> None:
        # Valid active key
        assert ApiAccess.objects.is_valid_key(self.key1)

        # Valid but inactive key
        assert not ApiAccess.objects.is_valid_key(self.key2)

        # Invalid key
        assert not ApiAccess.objects.is_valid_key("wrong_key")

    def test_get_by_key_or_none(self) -> None:
        # Valid active key
        found = ApiAccess.objects.get_by_key_or_none(self.key1)
        assert found == self.access1

        # Valid but inactive key
        found = ApiAccess.objects.get_by_key_or_none(self.key2)
        assert found is None

        # Invalid key
        found = ApiAccess.objects.get_by_key_or_none("wrong_key")
        assert found is None
