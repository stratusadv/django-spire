"""
Tests for RestQuerySet using DummyJSON Users API.
"""
from django.test import TestCase

from django_spire.contrib.rest.tests.example_users import UserSchema
from django_spire.contrib.rest.queryset import RestSchemaSet


class TestRestSchemaQuerySet(TestCase):
    """Test RestQuerySet functionality with DummyJSON Users API."""

    def test_queryset_iteration(self):
        users = list(UserSchema.objects.limit(5))

        self.assertLessEqual(len(users), 5)
        self.assertGreater(len(users), 0)

    def test_first(self):
        user = UserSchema.objects.first()

        self.assertIsNotNone(user)
        # First user should be Emily
        self.assertEqual(user.firstName, "Emily")

    def test_last(self):
        user = UserSchema.objects.limit(5).last()

        self.assertIsNotNone(user)

    def test_count(self):
        count = UserSchema.objects.limit(10).count()

        self.assertIsInstance(count, int)
        self.assertEqual(count, 10)

    def test_exists(self):
        self.assertTrue(UserSchema.objects.exists())

    def test_chaining_returns_new_queryset(self):
        qs1 = UserSchema.objects
        qs2 = qs1.filter(lambda x: True)
        qs3 = qs2.order_by("firstName")
        qs4 = qs3.limit(5)

        # Each should be a new instance (immutability)
        self.assertIsNot(qs1, qs2)
        self.assertIsNot(qs2, qs3)
        self.assertIsNot(qs3, qs4)
        self.assertTrue(all(isinstance(q, RestSchemaSet) for q in [qs1, qs2, qs3, qs4]))

    def test_filter_with_predicate(self):
        qs = UserSchema.objects.limit(10)

        # Filter to names starting with 'M'
        filtered = list(qs.filter(lambda u: u.firstName.startswith('M')))

        self.assertTrue(all(u.firstName.startswith('M') for u in filtered))
        self.assertGreater(len(filtered), 0)

    def test_filter_with_kwargs(self):
        qs = UserSchema.objects.limit(10)

        # Get first user and filter by username
        first = qs.first()
        if first:
            filtered = list(qs.filter(username=first.username))
            self.assertGreaterEqual(len(filtered), 1)
            self.assertEqual(filtered[0].username, first.username)

    def test_limit(self):
        users = list(UserSchema.objects.limit(3))

        self.assertEqual(len(users), 3)

    def test_offset(self):
        all_users = list(UserSchema.objects.limit(5))
        offset_users = list(UserSchema.objects.limit(5).offset(1))

        # offset(1) should skip the first result
        if len(all_users) > 1:
            self.assertEqual(offset_users[0].id, all_users[1].id)

    def test_order_by_ascending(self):
        users = list(UserSchema.objects.limit(10).order_by("firstName"))

        first_names = [u.firstName for u in users]
        self.assertEqual(first_names, sorted(first_names))

    def test_order_by_descending(self):
        users = list(UserSchema.objects.limit(10).order_by("-firstName"))

        first_names = [u.firstName for u in users]
        self.assertEqual(first_names, sorted(first_names, reverse=True))

    def test_values_list_flat(self):
        usernames = UserSchema.objects.limit(5).values_list("username", flat=True)

        self.assertIsInstance(usernames, list)
        self.assertTrue(all(isinstance(u, str) for u in usernames))
        self.assertEqual(len(usernames), 5)

    def test_values_list_tuple(self):
        values = UserSchema.objects.limit(5).values_list("firstName", "lastName")

        self.assertIsInstance(values, list)
        self.assertTrue(all(isinstance(v, tuple) and len(v) == 2 for v in values))

    def test_indexing(self):
        first = UserSchema.objects.limit(10)[0]

        self.assertIsNotNone(first)
        self.assertEqual(first.firstName, "Emily")

    def test_slicing(self):
        sliced = UserSchema.objects[0:3]

        self.assertIsInstance(sliced, RestSchemaSet)
        results = list(sliced)
        self.assertLessEqual(len(results), 3)

    def test_complex_chain(self):
        """Test a complex chain of operations."""
        results = list(
            UserSchema.objects
            .limit(20)
            .filter(lambda u: u.firstName is not None)
            .order_by("firstName")
            .limit(5)
        )

        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 5)

        # Should be sorted
        if len(results) > 1:
            first_names = [u.firstName for u in results]
            self.assertEqual(first_names, sorted(first_names))

    def test_exclude(self):
        """Test exclude functionality."""
        all_users = list(UserSchema.objects.limit(10))
        first_user = all_users[0]
        excluded = list(UserSchema.objects.limit(10).exclude(lambda u: u.id == first_user.id))

        # First user should not be in the excluded list
        self.assertTrue(all(u.id != first_user.id for u in excluded))
        # Should still get results (limit is applied after exclude)
        self.assertGreater(len(excluded), 0)

    def test_get(self):
        """Test get() method."""
        qs = UserSchema.objects.limit(10)

        # Get by username
        user = qs.get(username="emilys")

        self.assertEqual(user.username, "emilys")
        self.assertEqual(user.firstName, "Emily")

    def test_all(self):
        """Test all() method returns a new queryset."""
        qs1 = UserSchema.objects
        qs2 = qs1.all()

        self.assertIsNot(qs1, qs2)
        self.assertIsInstance(qs2, RestSchemaSet)
