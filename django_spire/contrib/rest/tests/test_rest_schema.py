"""
Tests for the new RestSchema class.
"""
from django.test import TestCase

from django_spire.contrib.rest.schema import RestSchema
from django_spire.contrib.rest.schemaset import RestSchemaSet


class UserSchema(RestSchema):
    """Test schema for DummyJSON Users API."""
    id: int
    firstName: str
    lastName: str
    email: str
    username: str

    class Meta:
        base_url = 'https://dummyjson.com'
        base_path = 'users'
        results_key = 'users'


class TestRestSchema(TestCase):
    """Tests for RestSchema base class."""

    def test_meta_configuration(self):
        """Test that Meta options are properly configured."""
        self.assertEqual(UserSchema._meta.base_url, 'https://dummyjson.com')
        self.assertEqual(UserSchema._meta.base_path, 'users')
        self.assertEqual(UserSchema._meta.results_key, 'users')

    def test_objects_returns_queryset(self):
        """Test that .objects returns a RestQuerySet."""
        qs = UserSchema.objects
        self.assertIsInstance(qs, RestSchemaSet)

    def test_fetch_one(self):
        """Test fetching a single user by ID."""
        user = UserSchema.fetch_one(1)

        self.assertIsInstance(user, UserSchema)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.firstName, "Emily")
        self.assertEqual(user.lastName, "Johnson")
        self.assertEqual(user.username, "emilys")

    def test_fetch_many(self):
        """Test fetching multiple users."""
        users = UserSchema.fetch_many(limit=5)

        self.assertIsInstance(users, list)
        self.assertEqual(len(users), 5)
        self.assertTrue(all(isinstance(u, UserSchema) for u in users))
        self.assertEqual(users[0].firstName, "Emily")

    def test_objects_all(self):
        """Test .objects.all() returns all results."""
        users = list(UserSchema.objects.limit(5).all())

        self.assertEqual(len(users), 5)
        self.assertTrue(all(isinstance(u, UserSchema) for u in users))

    def test_objects_first(self):
        """Test .objects.first() returns first result."""
        user = UserSchema.objects.first()

        self.assertIsNotNone(user)
        self.assertIsInstance(user, UserSchema)
        self.assertEqual(user.firstName, "Emily")

    def test_objects_filter(self):
        """Test .objects.filter() with lambda."""
        users = list(UserSchema.objects.limit(10).filter(lambda u: u.firstName.startswith('E')))

        self.assertGreater(len(users), 0)
        self.assertTrue(all(u.firstName.startswith('E') for u in users))

    def test_objects_limit(self):
        """Test .objects.limit() limits results."""
        users = list(UserSchema.objects.limit(3))

        self.assertEqual(len(users), 3)

    def test_objects_order_by(self):
        """Test .objects.order_by() orders results."""
        users = list(UserSchema.objects.limit(10).order_by('firstName'))

        first_names = [u.firstName for u in users]
        self.assertEqual(first_names, sorted(first_names))

    def test_objects_order_by_descending(self):
        """Test .objects.order_by() with descending."""
        users = list(UserSchema.objects.limit(10).order_by('-firstName'))

        first_names = [u.firstName for u in users]
        self.assertEqual(first_names, sorted(first_names, reverse=True))

    def test_objects_chaining(self):
        """Test method chaining."""
        users = list(
            UserSchema.objects
            .limit(10)
            .filter(lambda u: u.firstName is not None)
            .order_by('firstName')
            .limit(3)
        )

        self.assertLessEqual(len(users), 3)
        if len(users) > 1:
            first_names = [u.firstName for u in users]
            self.assertEqual(first_names, sorted(first_names))

    def test_objects_values_list(self):
        """Test .objects.values_list() extracts field values."""
        usernames = UserSchema.objects.limit(5).values_list('username', flat=True)

        self.assertIsInstance(usernames, list)
        self.assertEqual(len(usernames), 5)
        self.assertTrue(all(isinstance(u, str) for u in usernames))

    def test_objects_count(self):
        """Test .objects.count() returns count."""
        count = UserSchema.objects.limit(5).count()

        self.assertEqual(count, 5)

    def test_objects_exists(self):
        """Test .objects.exists() returns True when results exist."""
        self.assertTrue(UserSchema.objects.exists())

    def test_objects_indexing(self):
        """Test queryset indexing."""
        user = UserSchema.objects.limit(10)[0]

        self.assertIsInstance(user, UserSchema)
        self.assertEqual(user.firstName, "Emily")

    def test_objects_slicing(self):
        """Test queryset slicing."""
        sliced = UserSchema.objects[0:3]

        self.assertIsInstance(sliced, RestSchemaSet)
        users = list(sliced)
        self.assertLessEqual(len(users), 3)


class TestRestSchemaWithCustomParsing(TestCase):
    """Tests for RestSchema with custom parse methods."""

    def test_custom_parse_list_response(self):
        """Test that parse_list_response can be overridden."""

        class CustomUserSchema(RestSchema):
            id: int
            firstName: str

            class Meta:
                base_url = 'https://dummyjson.com'
                base_path = 'users'

            @classmethod
            def parse_list_response(cls, data: dict) -> list[dict]:
                # Custom extraction from 'users' key
                return data.get('users', [])[:3]  # Only first 3

        users = CustomUserSchema.fetch_many()

        self.assertEqual(len(users), 3)
        self.assertIsInstance(users[0], CustomUserSchema)
