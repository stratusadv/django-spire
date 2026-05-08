"""
Tests for the RestSchema class.
"""
from django.test import TestCase

from django_spire.contrib.rest import RestSchemaSet, RestSchema
from django_spire.contrib.rest.tests.example_users import UserSchema


class MockSchemaSet(RestSchemaSet['MockSchema']):
    """SchemaSet that returns controlled test data."""

    def __init__(self, data: list['MockSchema'] | None = None, **kwargs):
        super().__init__(**kwargs)
        self._mock_data = data or []

    def _clone(self, **overrides) -> 'MockSchemaSet':
        clone = super()._clone(**overrides)
        clone._mock_data = self._mock_data
        return clone

    def _read_many(self, **request_params) -> list['MockSchema']:
        return self._mock_data


class MockSchema(RestSchema):
    """Simple schema for testing distinct functionality."""
    id: int
    name: str
    category: str
    status: str

    objects = MockSchemaSet.as_manager()


class TestRestSchema(TestCase):
    """Tests for RestSchema base class."""

    def test_objects_returns_queryset(self):
        """Test that .objects returns a RestSchemaSet."""
        qs = UserSchema.objects
        self.assertIsInstance(qs, RestSchemaSet)

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


class TestRestSchemaSetDistinct(TestCase):
    """Tests for RestSchemaSet.distinct() method."""

    def setUp(self):
        """Set up test data with duplicates."""
        self.test_data = [
            MockSchema(id=1, name='Alice', category='admin', status='active'),
            MockSchema(id=2, name='Bob', category='user', status='active'),
            MockSchema(id=3, name='Alice', category='user', status='inactive'),
            MockSchema(id=4, name='Charlie', category='admin', status='active'),
            MockSchema(id=5, name='Bob', category='admin', status='active'),
            MockSchema(id=6, name='Alice', category='admin', status='active'),
        ]
        self.schema_set = MockSchemaSet(
            data=self.test_data,
            schema_class=MockSchema,
        )

    def test_distinct_single_field(self):
        """Test distinct on a single field removes duplicates."""
        results = list(self.schema_set.distinct('name'))

        names = [r.name for r in results]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(names), {'Alice', 'Bob', 'Charlie'})

    def test_distinct_single_field_preserves_first(self):
        """Test that distinct keeps the first occurrence."""
        results = list(self.schema_set.distinct('name'))

        alice = next(r for r in results if r.name == 'Alice')
        self.assertEqual(alice.id, 1)

    def test_distinct_multiple_fields(self):
        """Test distinct on multiple fields."""
        results = list(self.schema_set.distinct('name', 'category'))

        keys = [(r.name, r.category) for r in results]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertIn(('Alice', 'admin'), keys)
        self.assertIn(('Alice', 'user'), keys)
        self.assertIn(('Bob', 'user'), keys)
        self.assertIn(('Bob', 'admin'), keys)

    def test_distinct_no_fields_uses_all_attributes(self):
        """Test distinct with no fields uses all public attributes."""
        results = list(self.schema_set.distinct())

        self.assertEqual(len(results), 6)

    def test_distinct_no_fields_with_true_duplicates(self):
        """Test distinct with no fields removes exact duplicates."""
        data_with_duplicates = [
            MockSchema(id=1, name='Alice', category='admin', status='active'),
            MockSchema(id=1, name='Alice', category='admin', status='active'),
            MockSchema(id=2, name='Bob', category='user', status='active'),
        ]
        schema_set = MockSchemaSet(data=data_with_duplicates, schema_class=MockSchema)

        results = list(schema_set.distinct())

        self.assertEqual(len(results), 2)

    def test_distinct_chaining_with_filter(self):
        """Test distinct can be chained with filter."""
        results = list(
            self.schema_set
            .filter(status='active')
            .distinct('name')
        )

        names = [r.name for r in results]
        self.assertEqual(len(names), len(set(names)))
        self.assertTrue(all(r.status == 'active' for r in results))

    def test_distinct_chaining_with_order_by(self):
        """Test distinct respects prior ordering."""
        results = list(
            self.schema_set
            .order_by('id')
            .distinct('name')
        )

        alice = next(r for r in results if r.name == 'Alice')
        self.assertEqual(alice.id, 1)

        results_desc = list(
            self.schema_set
            .order_by('-id')
            .distinct('name')
        )

        alice_desc = next(r for r in results_desc if r.name == 'Alice')
        self.assertEqual(alice_desc.id, 6)

    def test_distinct_chaining_with_limit(self):
        """Test distinct can be chained with limit."""
        results = list(
            self.schema_set
            .distinct('name')
            .limit(2)
        )

        self.assertEqual(len(results), 2)

    def test_distinct_chaining_with_offset(self):
        """Test distinct can be chained with offset."""
        all_distinct = list(self.schema_set.distinct('name'))
        offset_results = list(self.schema_set.distinct('name').offset(1))

        self.assertEqual(len(offset_results), len(all_distinct) - 1)
        self.assertEqual(offset_results[0].name, all_distinct[1].name)

    def test_distinct_returns_new_schemaset(self):
        """Test that distinct returns a new SchemaSet instance."""
        original = self.schema_set
        distinct = original.distinct('name')

        self.assertIsNot(original, distinct)
        self.assertIsInstance(distinct, RestSchemaSet)

    def test_distinct_on_empty_set(self):
        """Test distinct on empty result set."""
        empty_set = MockSchemaSet(data=[], schema_class=MockSchema)

        results = list(empty_set.distinct('name'))

        self.assertEqual(results, [])
