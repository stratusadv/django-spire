import pytest
from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeding.field.seed.llm_seed import LlmFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestSeederStaticMethods(TestCase):
    def test_exclude_returns_exclude_field_seed(self):
        seed = Seeder.exclude()
        assert isinstance(seed, ExcludeFieldSeed)

    def test_static_with_string_value(self):
        seed = Seeder.static('hello')
        assert isinstance(seed, StaticFieldSeed)
        assert seed.generate_value(0) == 'hello'

    def test_static_with_int_value(self):
        seed = Seeder.static(42)
        assert seed.generate_value(0) == 42

    def test_static_with_bool_value(self):
        seed = Seeder.static(True)
        assert seed.generate_value(0) is True

    def test_static_with_none_value(self):
        seed = Seeder.static(None)
        assert seed.generate_value(0) is None

    def test_static_with_list_value(self):
        seed = Seeder.static([1, 2, 3])
        assert seed.generate_value(0) == [1, 2, 3]

    def test_llm_returns_llm_field_seed(self):
        seed = Seeder.llm(str)
        assert isinstance(seed, LlmFieldSeed)
        assert seed.field_type is str
        assert seed.prompt is None

    def test_llm_with_prompt(self):
        seed = Seeder.llm(str, 'Test prompt')
        assert isinstance(seed, LlmFieldSeed)
        assert seed.prompt == 'Test prompt'

    def test_llm_inherits_locale(self):
        class CustomSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}
            locale = 'fr_FR'

        seed = CustomSeeder.llm(str)
        assert isinstance(seed, LlmFieldSeed)
        assert seed.locale == 'fr_FR'


class TestSeederProperties(TestCase):
    def test_cache_name_format(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=1, verbose=False)
        assert seeder._cache_name == 'testseeder_cache'

    def test_cache_name_with_uppercase(self):
        class ABCSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = ABCSeeder(count=1, verbose=False)
        assert seeder._cache_name == 'abcseeder_cache'

    def test_name_verbose_single_word(self):
        class SimpleSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = SimpleSeeder(count=1, verbose=False)
        assert seeder.name_verbose == 'Simple Seeder'

    def test_name_verbose_all_caps(self):
        class APISeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = APISeeder(count=1, verbose=False)
        assert seeder.name_verbose == 'A P I Seeder'

    def test_name_verbose_mixed_case(self):
        class MyTestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = MyTestSeeder(count=1, verbose=False)
        assert 'My' in seeder.name_verbose
        assert 'Test' in seeder.name_verbose


class TestSeederSeedMethod(TestCase):
    def test_seed_count_n(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=3, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 3

    def test_seed_count_zero(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=0, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 0

    def test_seed_count_one(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=1, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 1

    def test_seed_with_override_count(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=1, verbose=False)
        seeder.seed(count=5)
        assert len(seeder.seeds) == 5

    def test_seed_populates_seeds_list(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=2, verbose=False)
        seeder.seed()
        for seed in seeder.seeds:
            assert hasattr(seed, 'to_dict')
            assert hasattr(seed, '__getitem__')

    def test_seed_calls_post_seed_hook(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

            def __post_seed__(self):
                self.hook_called = True

        seeder = TestSeeder(count=1, verbose=False)
        seeder.hook_called = False
        seeder.seed()
        assert seeder.hook_called is True

    def test_reseed_clears_and_regenerates(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=2, verbose=False)
        seeder.seed()
        original_count = len(seeder.seeds)

        seeder.reseed(count=5)
        assert len(seeder.seeds) == 5
        assert len(seeder.seeds) != original_count


class TestSeederOutputMethods(TestCase):
    def test_to_list_of_dicts(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=2, verbose=False)
        result = seeder.to_list_of_dicts()
        assert isinstance(result, list)
        assert len(result) == 2
        for item in result:
            assert isinstance(item, dict)
            assert 'name' in item

    def test_to_json_returns_string(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=1, verbose=False)
        result = seeder.to_list_of_dicts()
        assert isinstance(result, list)
        assert len(result) == 1

    def test_seed_class_instantiation(self):
        class SimpleClass:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=2, verbose=False)
        instances = seeder.seed_class(SimpleClass)
        assert len(instances) == 2
        for instance in instances:
            assert isinstance(instance, SimpleClass)
            assert instance.name == 'Test'


class TestSeederReset(TestCase):
    def test_reset_clears_seeds(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=3, verbose=False)
        seeder.seed()
        assert len(seeder.seeds) == 3
        seeder.reset()
        assert len(seeder.seeds) == 0

    def test_reset_clears_object_ids(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=2, verbose=False)
        seeder._model_object_ids = [1, 2]
        assert len(seeder._model_object_ids) == 2
        seeder.reset()
        assert len(seeder._model_object_ids) == 0

    def test_reset_can_be_called_multiple_times(self):
        class TestSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = TestSeeder(count=3, verbose=False)
        seeder.seed()
        seeder.reset()
        seeder.reset()
        seeder.reset()
        assert len(seeder.seeds) == 0