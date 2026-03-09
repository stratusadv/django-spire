from django.test import TestCase
from django_spire.api.tools import hash_string
from django_spire.conf import settings

class ToolsTestCase(TestCase):
    def test_hash_string(self):
        value = "test_key"
        hashed = hash_string(value)
        
        # Verify it's a hex string of expected length for SHA256 (64 chars)
        self.assertEqual(len(hashed), 64)
        
        # Verify consistency
        self.assertEqual(hashed, hash_string(value))
        
        # Verify it changes with different input
        self.assertNotEqual(hashed, hash_string("other_key"))
        
        # Verify it's not just the input
        self.assertNotEqual(hashed, value)
