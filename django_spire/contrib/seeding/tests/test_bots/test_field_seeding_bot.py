from django.test import TestCase

from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeding.field.seed.llm_seed import LlmFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed
from django_spire.contrib.seeding.intelligence.bots.field_seeding_bot import FieldSeedingBot
from django_spire.contrib.seeding.seed.seed import Seed


class TestFieldSeedingBot(TestCase):
    def test_instantiation(self):
        bot = FieldSeedingBot()
        assert bot is not None

    def test_process_returns_seed_object(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'name': StaticFieldSeed('Test'),
            'description': LlmFieldSeed(str, 'A description'),
        }
        result = bot.process(
            seeder_name='Test Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert isinstance(result, Seed)
        assert hasattr(result, 'to_dict')

    def test_process_includes_non_llm_fields(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'static_name': StaticFieldSeed('Static Name'),
            'static_count': StaticFieldSeed(42),
            'llm_description': LlmFieldSeed(str, 'A description'),
        }
        result = bot.process(
            seeder_name='Test Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert result['static_name'] == 'Static Name'
        assert result['static_count'] == 42

    def test_process_handles_exclude_fields(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'name': StaticFieldSeed('Test'),
            'excluded': ExcludeFieldSeed(),
        }
        result = bot.process(
            seeder_name='Test Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert 'name' in result.to_dict()
        assert 'excluded' not in result.to_dict()

    def test_process_with_no_llm_fields(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'name': StaticFieldSeed('Test'),
            'value': StaticFieldSeed(42),
        }
        result = bot.process(
            seeder_name='Test Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert isinstance(result, Seed)
        assert result['name'] == 'Test'
        assert result['value'] == 42

    def test_process_with_multiple_llm_fields(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'name': StaticFieldSeed('Test'),
            'field_a': LlmFieldSeed(str, 'Field A description'),
            'field_b': LlmFieldSeed(str),
            'field_c': LlmFieldSeed(int),
        }
        result = bot.process(
            seeder_name='Test Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert isinstance(result, Seed)
        assert result['name'] == 'Test'

    def test_process_preserves_static_values(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'active': StaticFieldSeed(value=True),
            'count': StaticFieldSeed(100),
            'status': StaticFieldSeed('complete'),
            'description': LlmFieldSeed(str),
        }
        result = bot.process(
            seeder_name='Test Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert result['active'] is True
        assert result['count'] == 100
        assert result['status'] == 'complete'

    def test_process_callable_field_seeds(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'random': CallableFieldSeed(callable_=lambda: 42),
            'description': LlmFieldSeed(str),
        }
        result = bot.process(
            seeder_name='Test Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert result['random'] == 42

    def test_process_returns_seed_for_various_fields(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'name': StaticFieldSeed('Test'),
            'value': StaticFieldSeed(42),
        }
        result = bot.process(
            seeder_name='Test Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert result is not None

    def test_llm_field_gets_filled_by_bot(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'name': StaticFieldSeed('Test'),
            'description': LlmFieldSeed(str, 'A creative description'),
        }
        result = bot.process(
            seeder_name='Test Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert result['name'] == 'Test'
        assert 'description' in result.to_dict() or hasattr(result, 'description')

    def test_process_with_prompt_field(self):
        bot = FieldSeedingBot()
        fields_seeds = {
            'custom_field': LlmFieldSeed(str, 'Create a unique creative value for this field'),
            'another_field': LlmFieldSeed(int),
        }
        result = bot.process(
            seeder_name='Custom Seeder',
            fields_seeds=fields_seeds,
            seed_index=0,
        )
        assert isinstance(result, Seed)


class TestFieldSeedingBotProcess(TestCase):
    def test_process_non_llm_fields_returns_values(self):
        result = FieldSeedingBot._process_non_llm_fields(
            fields_seeds={
                'static': StaticFieldSeed('static_value'),
                'callable': CallableFieldSeed(callable_=lambda: 123),
            },
            seed_index=0,
        )
        assert result['static'] == 'static_value'
        assert result['callable'] == 123

    def test_process_non_llm_fields_excludes_llm(self):
        result = FieldSeedingBot._process_non_llm_fields(
            fields_seeds={
                'static': StaticFieldSeed('value'),
                'llm': LlmFieldSeed(str),
            },
            seed_index=0,
        )
        assert 'static' in result
        assert 'llm' not in result

    def test_process_non_llm_fields_excludes_exclude(self):
        result = FieldSeedingBot._process_non_llm_fields(
            fields_seeds={
                'static': StaticFieldSeed('value'),
                'excluded': ExcludeFieldSeed(),
            },
            seed_index=0,
        )
        assert 'static' in result
        assert 'excluded' not in result