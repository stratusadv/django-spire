"""
Tests for the REST client architecture using RestSchema with DummyJSON Users API.
"""
from django.test import TestCase

from django_spire.contrib.rest import RestSchemaSet
from django_spire.contrib.rest.tests.example_users import UserSchema


class TestRestSchema(TestCase):
    """Test the RestSchema pattern with DummyJSON Users API."""

    def test_objects_descriptor(self):
        """Test that .objects returns a RestSchemaSet."""
        qs = UserSchema.objects

        self.assertIsInstance(qs, RestSchemaSet)

    def test_objects_first_returns_schema(self):
        """Test that .objects.first() returns a UserSchema instance."""
        user = UserSchema.objects.first()

        self.assertIsInstance(user, UserSchema)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.firstName, "Emily")
        self.assertEqual(user.lastName, "Johnson")
        self.assertEqual(user.username, "emilys")

    def test_objects_limit(self):
        """Test that .objects.limit() limits results."""
        users = list(UserSchema.objects.limit(5))

        self.assertEqual(len(users), 5)
        self.assertTrue(all(isinstance(u, UserSchema) for u in users))

    def test_objects_iteration(self):
        """Test that .objects can be iterated."""
        users = list(UserSchema.objects.limit(3))

        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], UserSchema)
