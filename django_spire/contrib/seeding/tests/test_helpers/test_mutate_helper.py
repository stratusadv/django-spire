from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.mutate.corrupt_seed import CorruptMutateFieldSeed
from django_spire.contrib.seeding.field.seed.mutate.choices import MutateSeverity
from django_spire.contrib.seeding.field.seed.mutate.nullable_seed import NullableMutateFieldSeed
from django_spire.contrib.seeding.field.seed.mutate.transform_seed import TransformMutateFieldSeed
from django_spire.contrib.seeding.field.seed.mutate.transform_seed import TypeCoercionMutateFieldSeed


class TestMutateFieldSeedHelper(TestCase):
    def test_corrupt_returns_corrupt_field_seed(self):
        seed = Seeder.static('hello')
        result = Seeder.mutate.corrupt(seed, corrupt_chance=0.5)
        assert isinstance(result, CorruptMutateFieldSeed)

    def test_corrupt_stores_field_seed(self):
        seed = Seeder.fake.name()
        result = Seeder.mutate.corrupt(seed, corrupt_chance=0.3)
        assert result.field_seed is seed

    def test_corrupt_stores_corrupt_chance(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.corrupt(seed, corrupt_chance=0.7)
        assert result.corrupt_chance == 0.7

    def test_corrupt_stores_severity_mild(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.corrupt(seed, severity=MutateSeverity.MILD)
        assert result.severity == MutateSeverity.MILD

    def test_corrupt_stores_severity_moderate(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.corrupt(seed, severity=MutateSeverity.MODERATE)
        assert result.severity == MutateSeverity.MODERATE

    def test_corrupt_stores_severity_chaos(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.corrupt(seed, severity=MutateSeverity.CHAOS)
        assert result.severity == MutateSeverity.CHAOS

    def test_corrupt_default_chance(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.corrupt(seed)
        assert result.corrupt_chance == 0.5

    def test_corrupt_default_severity(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.corrupt(seed)
        assert result.severity == MutateSeverity.MILD

    def test_nullable_returns_nullable_field_seed(self):
        seed = Seeder.static('hello')
        result = Seeder.mutate.nullable(seed, nullify_chance=0.5)
        assert isinstance(result, NullableMutateFieldSeed)

    def test_nullable_stores_field_seed(self):
        seed = Seeder.fake.name()
        result = Seeder.mutate.nullable(seed, nullify_chance=0.3)
        assert result.field_seed is seed

    def test_nullable_stores_nullify_chance(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.nullable(seed, nullify_chance=0.7)
        assert result.nullify_chance == 0.7

    def test_nullable_default_chance(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.nullable(seed)
        assert result.nullify_chance == 0.5

    def test_value_returns_transform_field_seed(self):
        seed = Seeder.static('hello')
        result = Seeder.mutate.value(seed, transform=str.upper)
        assert isinstance(result, TransformMutateFieldSeed)

    def test_value_stores_field_seed(self):
        seed = Seeder.fake.name()
        result = Seeder.mutate.value(seed, transform=str.lower)
        assert result.field_seed is seed

    def test_value_stores_transform(self):
        seed = Seeder.static('Hello World')
        result = Seeder.mutate.value(seed, transform=str.lower, change_chance=1.0)
        assert result.transform is str.lower
        assert result.generate_value(0) == 'hello world'

    def test_value_stores_change_chance(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.value(seed, transform=str.upper, change_chance=0.8)
        assert result.change_chance == 0.8

    def test_value_default_chance(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.value(seed, transform=str.upper)
        assert result.change_chance == 0.5

    def test_type_returns_type_coercion_field_seed(self):
        seed = Seeder.static('123')
        result = Seeder.mutate.type(seed, target_type=int)
        assert isinstance(result, TypeCoercionMutateFieldSeed)

    def test_type_stores_field_seed(self):
        seed = Seeder.fake.sentence()
        result = Seeder.mutate.type(seed, target_type=str)
        assert result.field_seed is seed

    def test_type_stores_target_type(self):
        seed = Seeder.static('42')
        result = Seeder.mutate.type(seed, target_type=int)
        assert result.target_type is int

    def test_type_stores_change_chance(self):
        seed = Seeder.static('123')
        result = Seeder.mutate.type(seed, target_type=int, change_chance=0.8)
        assert result.change_chance == 0.8

    def test_type_default_chance(self):
        seed = Seeder.static('123')
        result = Seeder.mutate.type(seed, target_type=int)
        assert result.change_chance == 0.5

    def test_type_coerces_to_int(self):
        seed = Seeder.static('123')
        result = Seeder.mutate.type(seed, target_type=int, change_chance=1.0)
        assert result.generate_value(0) == 123

    def test_type_coerces_to_float(self):
        seed = Seeder.static('3.14')
        result = Seeder.mutate.type(seed, target_type=float, change_chance=1.0)
        assert result.generate_value(0) == 3.14


class TestMutateFieldSeedHelperStacked(TestCase):
    def test_nullable_around_corrupt(self):
        seed = Seeder.static('value')
        result = Seeder.mutate.nullable(
            Seeder.mutate.corrupt(seed, corrupt_chance=1.0), nullify_chance=0.0
        )
        assert isinstance(result, NullableMutateFieldSeed)
        assert isinstance(result.field_seed, CorruptMutateFieldSeed)

    def test_transform_around_nullable(self):
        seed = Seeder.static('HELLO')
        result = Seeder.mutate.value(
            Seeder.mutate.nullable(seed, nullify_chance=0.0), transform=str.lower, change_chance=1.0
        )
        assert result.generate_value(0) == 'hello'

    def test_type_after_transform(self):
        seed = Seeder.static('42')
        result = Seeder.mutate.type(
            Seeder.mutate.value(seed, transform=lambda v: v.strip(), change_chance=1.0),
            target_type=int,
            change_chance=1.0,
        )
        assert result.generate_value(0) == 42

    def test_corrupt_after_nullable(self):
        seed = Seeder.static('test_value')
        result = Seeder.mutate.corrupt(
            Seeder.mutate.nullable(seed, nullify_chance=0.0),
            corrupt_chance=1.0,
            severity=MutateSeverity.MILD,
        )
        assert isinstance(result, CorruptMutateFieldSeed)

    def test_three_layers(self):
        seed = Seeder.static('deep')
        result = Seeder.mutate.nullable(
            Seeder.mutate.value(seed, transform=str.upper, change_chance=1.0),
            nullify_chance=0.0,
        )
        assert isinstance(result, NullableMutateFieldSeed)
        assert isinstance(result.field_seed, TransformMutateFieldSeed)

    def test_corrupt_with_chaos_severity(self):
        seed = Seeder.static('chaos_value')
        result = Seeder.mutate.corrupt(
            seed, corrupt_chance=1.0, severity=MutateSeverity.CHAOS
        )
        assert result.severity == MutateSeverity.CHAOS