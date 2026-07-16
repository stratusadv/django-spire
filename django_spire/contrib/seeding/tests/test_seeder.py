import json
import random

import pytest
from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError

from test_project.app.task.choices import TaskStatusChoices
from test_project.app.task.models import Task


def random_boolean(true_weight: float = 0.5) -> bool:
    return random.random() <= true_weight


class TaskSeeder(Seeder):
    model_class = Task
    cache_enabled = False
    fields_seeds = {
        'name': Seeder.fake.sentence(),
        'status': Seeder.model.random_field_choice(TaskStatusChoices),
        'description': Seeder.llm(str),
        'created_datetime': Seeder.fake.date_time_between(start_date='-30d', end_date='now'),
        'is_active': Seeder.static(value=True),
        'is_deleted': Seeder.custom.callable(random_boolean, true_weight=0.8),
    }


class TestSeederValidation(TestCase):
    def test_subclass_without_fields_seeds_raises(self):
        with pytest.raises(ValueError, match='fields_seeds is None'):

            class NoFieldsSeeder(Seeder):
                pass

    def test_fields_seeds_keys_must_be_strings(self):
        with pytest.raises(DjangoSpireSeederError) as ctx:

            class BadKeySeeder(TaskSeeder):
                fields_seeds = {123: Seeder.static('value')}

        assert 'must all be strings' in str(ctx.value)

    def test_fields_seeds_values_must_be_base_field_seed(self):
        with pytest.raises(DjangoSpireSeederError) as ctx:

            class BadValueSeeder(TaskSeeder):
                fields_seeds = {'name': 'not a field seed'}

        assert 'must all be BaseFieldSeed' in str(ctx.value)


class TestSeederProperties(TestCase):
    def test_cache_name_format(self):
        seeder = TaskSeeder(count=1, verbose=False)
        assert seeder._cache_name == 'taskseeder_cache'

    def test_name_verbose_single_word(self):
        seeder = TaskSeeder(count=1, verbose=False)
        assert seeder.name_verbose == 'Task Seeder'

    def test_name_verbose_all_caps(self):
        class APISeeder(TaskSeeder):
            pass

        seeder = APISeeder(count=1, verbose=False)
        assert seeder.name_verbose == 'A P I Seeder'


class TestSeederSeed(TestCase):
    def test_seed_count_n(self):
        seeder = TaskSeeder(count=3, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 3

    def test_seed_count_zero(self):
        seeder = TaskSeeder(count=0, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 0

    def test_seed_count_one(self):
        seeder = TaskSeeder(count=1, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 1

    def test_seed_with_override_count(self):
        seeder = TaskSeeder(count=1, verbose=False)
        seeder.seed(count=5)
        assert len(seeder.seeds) == 5

    def test_seed_populates_seeds_list(self):
        seeder = TaskSeeder(count=2, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert hasattr(seed, 'to_dict')
            assert hasattr(seed, '__getitem__')

    def test_seed_calls_post_seed_hook(self):
        hook_called = []

        class HookSeeder(TaskSeeder):
            def __post_seed__(self) -> None:
                hook_called.append(True)

        seeder = HookSeeder(count=1, verbose=False)
        seeder.seed()
        assert hook_called == [True]

    def test_reseed_clears_and_regenerates(self):
        seeder = TaskSeeder(count=2, verbose=False)
        seeder.seed()
        original_seeds = list(seeder.seeds)

        seeder.reseed(count=3)
        assert len(seeder.seeds) == 3
        assert seeder.seeds != original_seeds


class TestSeederOutput(TestCase):
    def test_to_list_of_dicts(self):
        seeder = TaskSeeder(count=2, verbose=False)
        result = seeder.to_list_of_dicts()
        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            assert isinstance(item, dict)
            assert 'name' in item
            assert 'status' in item

    def test_to_json_is_valid_json(self):
        seeder = TaskSeeder(count=1, verbose=False)
        result = seeder.to_json()
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) == 1

    def test_to_model_instances(self):
        seeder = TaskSeeder(count=2, verbose=False)
        instances = seeder.to_model_instances()
        assert len(instances) == 2
        for instance in instances:
            assert isinstance(instance, Task)

    def test_seed_class_instantiation(self):
        seeder = TaskSeeder(count=1, verbose=False)
        instances = seeder.seed_class(Task)
        assert len(instances) == 1
        assert isinstance(instances[0], Task)


class TestSeederDatabase(TestCase):
    def test_seed_database_requires_model_class(self):
        class NoModelSeeder(Seeder):
            fields_seeds = {'name': Seeder.fake.sentence()}

        seeder = NoModelSeeder(count=1, verbose=False)
        with pytest.raises(DjangoSpireSeederError) as ctx:
            seeder.seed_database()

        assert 'Cannot seed database without a model class' in str(ctx.value)

    def test_seed_database_creates_records(self):
        initial_count = Task.objects.count()
        seeder = TaskSeeder(count=3, verbose=False)
        result = seeder.seed_database()
        assert Task.objects.count() == initial_count + 3
        assert result.count() == 3

    def test_seed_database_stores_ids(self):
        seeder = TaskSeeder(count=2, verbose=False)
        seeder.seed_database()
        assert len(seeder._model_object_ids) == 2

    def test_seed_database_queryset_returns_seeded(self):
        seeder = TaskSeeder(count=2, verbose=False)
        seeder.seed_database()
        qs = seeder.queryset
        assert qs.count() == 2
        pks = list(qs.values_list('pk', flat=True))
        assert seeder._model_object_ids[0] in pks
        assert seeder._model_object_ids[1] in pks

    def test_seed_database_calls_post_hook(self):
        hook_called = []

        class HookSeeder(TaskSeeder):
            def __post_seed_database__(self) -> None:
                hook_called.append(True)

        seeder = HookSeeder(count=1, verbose=False)
        seeder.seed_database()
        assert hook_called == [True]

    def test_reseed_database(self):
        seeder = TaskSeeder(count=2, verbose=False)
        seeder.seed_database()
        initial_pks = set(seeder._model_object_ids)

        seeder.reseed_database(count=3)
        assert len(seeder._model_object_ids) == 3
        assert set(seeder._model_object_ids) != initial_pks


class TestSeederQueryset(TestCase):
    def test_queryset_property(self):
        seeder = TaskSeeder(count=2, verbose=False)
        seeder.seed_database()
        qs = seeder.queryset
        assert qs.count() == 2
        assert set(qs.values_list('pk', flat=True)) == set(seeder._model_object_ids)

    def test_queryset_requires_model_class(self):
        class NoModelSeeder(Seeder):
            fields_seeds = {'name': Seeder.fake.sentence()}

        seeder = NoModelSeeder(count=1, verbose=False)
        seeder.seeds = []
        with pytest.raises(DjangoSpireSeederError) as ctx:
            _ = seeder.queryset

        assert 'Cannot create queryset without a model class' in str(ctx.value)


class TestSeederReset(TestCase):
    def test_reset_clears_seeds(self):
        seeder = TaskSeeder(count=3, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 3
        seeder.reset()
        assert len(seeder.seeds) == 0

    def test_reset_clears_object_ids(self):
        seeder = TaskSeeder(count=2, verbose=False)
        seeder.seed_database()
        assert len(seeder._model_object_ids) == 2
        seeder.reset()
        assert len(seeder._model_object_ids) == 0
