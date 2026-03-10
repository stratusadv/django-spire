from django.test import TestCase

from django_spire.api.tools import hash_string


class ToolsTestCase(TestCase):
    def test_hash_string(self) -> None:
        value = 'test_key'
        hashed = hash_string(value)

        # Verify it's a hex string of expected length for SHA256 (64 chars)
        assert len(hashed) == 64

        # Verify consistency
        assert hashed == hash_string(value)

        # Verify it changes with different input
        assert hashed != hash_string('other_key')

        # Verify it's not just the input
        assert hashed != value
