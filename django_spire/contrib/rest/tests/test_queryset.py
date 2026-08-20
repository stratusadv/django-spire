"""
Tests for RestQuerySet using DummyJSON Users API.
"""

from django.test import TestCase

from django_spire.contrib.rest import RestSchemaSet
from django_spire.contrib.rest.tests.example_users import UserSchema


class TestRestSchemaQuerySet(TestCase):
    """Test RestQuerySet functionality with DummyJSON Users API."""

    def test_queryset_iteration(self):
        users = list(UserSchema.objects.limit(5))

        assert len(users) <= 5
        assert len(users) > 0

    def test_first(self):
        user = UserSchema.objects.first()

        assert user is not None
        # First user should be Emily
        assert user.firstName == 'Emily'

    def test_last(self):
        user = UserSchema.objects.limit(5).last()

        assert user is not None

    def test_count(self):
        count = UserSchema.objects.limit(10).count()

        assert isinstance(count, int)
        assert count == 10

    def test_exists(self):
        assert UserSchema.objects.exists()

    def test_chaining_returns_new_queryset(self):
        qs1 = UserSchema.objects
        qs2 = qs1.filter(lambda x: True)
        qs3 = qs2.order_by('firstName')
        qs4 = qs3.limit(5)

        # Each should be a new instance (immutability)
        assert qs1 is not qs2
        assert qs2 is not qs3
        assert qs3 is not qs4
        assert all(isinstance(q, RestSchemaSet) for q in [qs1, qs2, qs3, qs4])

    def test_filter_with_predicate(self):
        qs = UserSchema.objects.limit(10)

        # Filter to names starting with 'M'
        filtered = list(qs.filter(lambda u: u.firstName.startswith('M')))

        assert all(u.firstName.startswith('M') for u in filtered)
        assert len(filtered) > 0

    def test_filter_with_kwargs(self):
        qs = UserSchema.objects.limit(10)

        # Get first user and filter by username
        first = qs.first()
        if first:
            filtered = list(qs.filter(username=first.username))
            assert len(filtered) >= 1
            assert filtered[0].username == first.username

    def test_limit(self):
        users = list(UserSchema.objects.limit(3))

        assert len(users) == 3

    def test_offset(self):
        all_users = list(UserSchema.objects.limit(5))
        offset_users = list(UserSchema.objects.limit(5).offset(1))

        # offset(1) should skip the first result
        if len(all_users) > 1:
            assert offset_users[0].id == all_users[1].id

    def test_order_by_ascending(self):
        users = list(UserSchema.objects.limit(10).order_by('firstName'))

        first_names = [u.firstName for u in users]
        assert first_names == sorted(first_names)

    def test_order_by_descending(self):
        users = list(UserSchema.objects.limit(10).order_by('-firstName'))

        first_names = [u.firstName for u in users]
        assert first_names == sorted(first_names, reverse=True)

    def test_values_list_flat(self):
        usernames = UserSchema.objects.limit(5).values_list('username', flat=True)

        assert isinstance(usernames, list)
        assert all(isinstance(u, str) for u in usernames)
        assert len(usernames) == 5

    def test_values_list_tuple(self):
        values = UserSchema.objects.limit(5).values_list('firstName', 'lastName')

        assert isinstance(values, list)
        assert all(isinstance(v, tuple) and len(v) == 2 for v in values)

    def test_indexing(self):
        first = UserSchema.objects.limit(10)[0]

        assert first is not None
        assert first.firstName == 'Emily'

    def test_slicing(self):
        sliced = UserSchema.objects[0:3]

        assert isinstance(sliced, RestSchemaSet)
        results = list(sliced)
        assert len(results) <= 3

    def test_complex_chain(self):
        """Test a complex chain of operations."""
        results = list(
            UserSchema.objects.limit(20)
            .filter(lambda u: u.firstName is not None)
            .order_by('firstName')
            .limit(5)
        )

        assert isinstance(results, list)
        assert len(results) <= 5

        # Should be sorted
        if len(results) > 1:
            first_names = [u.firstName for u in results]
            assert first_names == sorted(first_names)

    def test_exclude(self):
        """Test exclude functionality."""
        all_users = list(UserSchema.objects.limit(10))
        first_user = all_users[0]
        excluded = list(UserSchema.objects.limit(10).exclude(lambda u: u.id == first_user.id))

        # First user should not be in the excluded list
        assert all(u.id != first_user.id for u in excluded)
        # Should still get results (limit is applied after exclude)
        assert len(excluded) > 0

    def test_get(self):
        """Test get() method."""
        qs = UserSchema.objects.limit(10)

        # Get by username
        user = qs.get(username='emilys')

        assert user.username == 'emilys'
        assert user.firstName == 'Emily'

    def test_all(self):
        """Test all() method returns a new queryset."""
        qs1 = UserSchema.objects
        qs2 = qs1.all()

        assert qs1 is not qs2
        assert isinstance(qs2, RestSchemaSet)
