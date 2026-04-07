"""
Tests for the REST client architecture using DummyJSON Users API.
"""
from django.test import TestCase

from django_spire.contrib.rest.tests.example_users import (
    DummyJsonUserClient,
    UserSchema,
)
from django_spire.contrib.rest.queryset import RestQuerySet


class TestDummyJsonUserClient(TestCase):
    """Test the DummyJSON User client with the REST architecture."""

    def test_client_initialization(self):
        client = DummyJsonUserClient()
        self.assertEqual(client.base_url, 'https://dummyjson.com')
        self.assertEqual(client.base_path, 'users')

    def test_fetch_one_by_id(self):
        client = DummyJsonUserClient()
        user = client.fetch_one(1)

        self.assertIsInstance(user, UserSchema)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.firstName, "Emily")
        self.assertEqual(user.lastName, "Johnson")
        self.assertEqual(user.username, "emilys")

    def test_fetch_one_different_user(self):
        client = DummyJsonUserClient()
        user = client.fetch_one(2)

        self.assertIsInstance(user, UserSchema)
        self.assertEqual(user.id, 2)
        # User 2 should have different data than user 1
        self.assertNotEqual(user.firstName, "Emily")

    def test_fetch_many(self):
        client = DummyJsonUserClient()
        users = client.fetch_many(limit=5)

        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 5)
        self.assertTrue(all(isinstance(u, UserSchema) for u in users))
        # First user should be Emily
        self.assertEqual(users[0].firstName, "Emily")

    def test_fetch_many_with_skip(self):
        client = DummyJsonUserClient()
        users = client.fetch_many(limit=3, skip=2)

        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 3)
        # Should start from user ID 3 (skipping first 2)
        self.assertEqual(users[0].id, 3)

    def test_objects_descriptor(self):
        client = DummyJsonUserClient()
        qs = client.objects

        self.assertIsInstance(qs, RestQuerySet)
