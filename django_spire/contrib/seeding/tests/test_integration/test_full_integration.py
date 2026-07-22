import enum
import pytest
from django.db import models
from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeding.field.seed.llm_seed import LlmFieldSeed
from django_spire.contrib.seeding.field.seed.random_seed import RandomEnumFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class StatusChoices(enum.Enum):
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETED = 'completed'


class FullTestSeeder(Seeder):
    model_class = None
    cache_enabled = False
    locale = 'en_CA'
    fields_seeds = {
        'name': Seeder.fake.name(),
        'status': Seeder.random.enum(StatusChoices),
        'count': Seeder.random.int(a=1, b=100),
        'active': Seeder.static(True),
        'description': Seeder.llm(str, 'A creative description'),
        'created': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
    }


class ChaosSeeder(Seeder):
    model_class = None
    cache_enabled = False
    fields_seeds = {
        'name': Seeder.mutate.corrupt(
            Seeder.fake.name(),
            corrupt_chance=0.3,
            severity=Seeder.mutate.Severity.CHAOS,
        ),
        'description': Seeder.llm(str),
        'status': Seeder.random.enum(StatusChoices),
        'active': Seeder.static(True),
    }


class LlmOnlySeeder(Seeder):
    model_class = None
    cache_enabled = False
    fields_seeds = {
        'field_a': Seeder.exclude(),
        'field_b': Seeder.llm(str, 'Field B description'),
        'field_c': Seeder.llm(int),
        'field_d': Seeder.llm(str),
    }


class ModifiedSeeder(Seeder):
    model_class = None
    cache_enabled = False
    fields_seeds = {
        'name': Seeder.fake.name(),
        'value': Seeder.static('original'),
        'description': Seeder.llm(str),
    }

    def __post_seed__(self):
        for seed in self.seeds:
            seed['name'] = 'Modified Name'
            seed['value'] = 'modified_value'


class TestFullIntegration(TestCase):
    def test_all_field_types_populated(self):
        seeder = FullTestSeeder(count=2, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert 'name' in seed.to_dict()
            assert 'status' in seed.to_dict()
            assert 'count' in seed.to_dict()
            assert 'active' in seed.to_dict()
            assert 'description' in seed.to_dict()
            assert 'created' in seed.to_dict()

    def test_faker_provider_returns_names(self):
        seeder = FullTestSeeder(count=3, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert 'name' in seed.to_dict()
            assert isinstance(seed['name'], str)

    def test_static_values_consistent(self):
        seeder = FullTestSeeder(count=5, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert seed['active'] is True

    def test_random_values_in_range(self):
        seeder = FullTestSeeder(count=20, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert 1 <= seed['count'] <= 100

    def test_llm_fields_filled_by_bot(self):
        seeder = FullTestSeeder(count=2, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert 'description' in seed.to_dict()

    def test_post_seed_hook_modifies_seeds(self):
        seeder = ModifiedSeeder(count=2, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert seed['name'] == 'Modified Name'
            assert seed['value'] == 'modified_value'

    def test_chaos_corruption_with_llm(self):
        seeder = ChaosSeeder(count=5, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 5
        for seed in seeder.seeds:
            assert 'description' in seed.to_dict()

    def test_only_llm_fields_filled(self):
        seeder = LlmOnlySeeder(count=2, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert 'field_b' in seed.to_dict()
            assert 'field_c' in seed.to_dict()
            assert 'field_d' in seed.to_dict()

    def test_exclude_field_not_in_seed(self):
        seeder = LlmOnlySeeder(count=1, verbose=False)
        seeder.seed()
        seed = seeder.seeds[0]
        assert 'field_a' not in seed.to_dict()

    def test_reseed_produces_new_seeds(self):
        seeder = FullTestSeeder(count=3, verbose=False)
        seeder.seed()
        original_seeds = [seed.to_dict() for seed in seeder.seeds]

        seeder.reseed(count=3)
        new_seeds = [seed.to_dict() for seed in seeder.seeds]

        assert len(new_seeds) == len(original_seeds)

    def test_to_list_of_dicts_format(self):
        seeder = FullTestSeeder(count=3, verbose=False)
        result = seeder.to_list_of_dicts()
        assert isinstance(result, list)
        assert len(result) == 3
        for item in result:
            assert isinstance(item, dict)

    def test_zero_count_produces_empty_seeds(self):
        seeder = FullTestSeeder(count=0, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 0

    def test_single_count_produces_one_seed(self):
        seeder = FullTestSeeder(count=1, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 1

    def test_nested_mutations(self):
        class NestedSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {
                'base': Seeder.static('base_value'),
                'transformed': Seeder.mutate.value(
                    Seeder.static('original'),
                    transform=str.upper,
                    change_chance=1.0,
                ),
                'nullable': Seeder.mutate.nullable(
                    Seeder.static('nullable_value'),
                    nullify_chance=0.0,
                ),
                'description': Seeder.llm(str),
            }

        seeder = NestedSeeder(count=1, verbose=False)
        seeder.seed()
        seed = seeder.seeds[0]
        assert seed['base'] == 'base_value'
        assert seed['transformed'] == 'ORIGINAL'
        assert seed['nullable'] == 'nullable_value'


class TestIntegrationWithDatabase(TestCase):
    @pytest.mark.django_db
    def test_to_model_instances_creates_instances(self):
        from django.db import models

        class TestModel(models.Model):
            name = models.CharField(max_length=100)
            value = models.IntegerField()

            class Meta:
                app_label = 'seeding_test'

        class DbSeeder(Seeder):
            model_class = TestModel
            cache_enabled = False
            fields_seeds = {
                'name': StaticFieldSeed('Test'),
                'value': StaticFieldSeed(42),
            }

        seeder = DbSeeder(count=2, verbose=False)
        instances = seeder.to_model_instances()
        assert len(instances) == 2
        for instance in instances:
            assert isinstance(instance, TestModel)
            assert instance.name == 'Test'
            assert instance.value == 42