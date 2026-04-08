"""
Tests for the REST client architecture using RestSchema with DummyJSON Users API.
"""
from django.test import TestCase

from django_spire.contrib.rest.tests.example_users import UserSchema
from django_spire.contrib.rest.queryset import RestSchemaSet


class TestRestSchemaClient(TestCase):
    """Test the RestSchema pattern with DummyJSON Users API."""

    def test_schema_meta_configuration(self):
        self.assertEqual(UserSchema._meta.base_url, 'https://dummyjson.com')
        self.assertEqual(UserSchema._meta.base_path, 'users')
        self.assertEqual(UserSchema._meta.results_key, 'users')

    def test_fetch_one_by_id(self):
        user = UserSchema.fetch_one(1)

        self.assertIsInstance(user, UserSchema)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.firstName, "Emily")
        self.assertEqual(user.lastName, "Johnson")
        self.assertEqual(user.username, "emilys")

    def test_fetch_one_different_user(self):
        user = UserSchema.fetch_one(2)

        self.assertIsInstance(user, UserSchema)
        self.assertEqual(user.id, 2)
        # User 2 should have different data than user 1
        self.assertNotEqual(user.firstName, "Emily")

    def test_fetch_many(self):
        users = UserSchema.fetch_many(limit=5)

        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 5)
        self.assertTrue(all(isinstance(u, UserSchema) for u in users))
        # First user should be Emily
        self.assertEqual(users[0].firstName, "Emily")

    def test_fetch_many_with_skip(self):
        users = UserSchema.fetch_many(limit=3, skip=2)

        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        # Should start from user ID 3 (skipping first 2)
        self.assertEqual(users[0].id, 3)

    def test_objects_descriptor(self):
        qs = UserSchema.objects

        self.assertIsInstance(qs, RestSchemaSet)
