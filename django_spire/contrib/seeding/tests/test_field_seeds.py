import pytest
from django.test import TestCase

from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeding.field.seed.llm_seed import LlmFieldSeed
from django_spire.contrib.seeding.field.seed.model_seed import OrderedForeignKeyModelFieldSeed
from django_spire.contrib.seeding.field.seed.random_seed import RandomFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed
from django_spire.contrib.seeding.seed.seed import Seed

from test_project.app.task.choices import TaskStatusChoices


class TestExcludeFieldSeed(TestCase):
    def test_generate_value_returns_none(self):
        seed = ExcludeFieldSeed()
        assert seed.generate_value() is None


class TestStaticFieldSeed(TestCase):
    def test_generate_value_returns_string(self):
        seed = StaticFieldSeed('hello')
        assert seed.generate_value() == 'hello'

    def test_generate_value_returns_int(self):
        seed = StaticFieldSeed(42)
        assert seed.generate_value() == 42

    def test_generate_value_returns_bool(self):
        seed = StaticFieldSeed(value=True)
        assert seed.generate_value() is True

    def test_generate_value_returns_list(self):
        seed = StaticFieldSeed([1, 2, 3])
        assert seed.generate_value() == [1, 2, 3]

    def test_generate_value_returns_dict(self):
        seed = StaticFieldSeed({'a': 1})
        assert seed.generate_value() == {'a': 1}

    def test_generate_value_returns_none(self):
        seed = StaticFieldSeed(None)
        assert seed.generate_value() is None

    def test_generate_value_returns_choice(self):
        seed = StaticFieldSeed(TaskStatusChoices.NEW)
        assert seed.generate_value() == TaskStatusChoices.NEW


class TestCallableFieldSeed(TestCase):
    def test_no_wrapper_calls_callable(self):
        seed = CallableFieldSeed(callable_=len, kwargs={'obj': 'hello'})
        assert seed.generate_value() == 5

    def test_with_wrapper_applies_wrapper(self):
        def uppercase(value: str) -> str:
            return value.upper()

        seed = CallableFieldSeed(callable_=lambda: 'hello', wrapper=uppercase)
        assert seed.generate_value() == 'HELLO'

    def test_wrapper_receives_callable_result(self):
        def add_exclamation(value: str) -> str:
            return f'{value}!'

        seed = CallableFieldSeed(callable_=lambda: 'hello', wrapper=add_exclamation)
        assert seed.generate_value() == 'hello!'

    def test_callable_with_multiple_kwargs(self):
        seed = CallableFieldSeed(callable_=pow, kwargs={'base': 2, 'exp': 3})
        assert seed.generate_value() == 8


class TestLlmFieldSeed(TestCase):
    def test_generate_value_returns_none(self):
        seed = LlmFieldSeed(field_type=str, prompt='Some prompt')
        assert seed.generate_value() is None

    def test_init_stores_field_type(self):
        seed = LlmFieldSeed(field_type=str)
        assert seed.field_type is str

    def test_init_stores_prompt(self):
        seed = LlmFieldSeed(field_type=str, prompt='Test prompt')
        assert seed.prompt == 'Test prompt'

    def test_init_stores_locale(self):
        seed = LlmFieldSeed(field_type=str, locale='en_US')
        assert seed.locale == 'en_US'


class TestRandomFieldSeed(TestCase):
    def test_with_enum_returns_enum_member(self):
        seed = RandomFieldSeed(enum_=TaskStatusChoices)
        value = seed.generate_value()
        assert value in list(TaskStatusChoices)

    def test_without_enum_returns_none(self):
        seed = RandomFieldSeed()
        assert seed.generate_value() is None


class TestOrderedForeignKeyModelFieldSeed(TestCase):
    def test_init_stores_foreign_keys(self):
        seed = OrderedForeignKeyModelFieldSeed(model_foreign_keys=[1, 2, 3])
        assert seed.model_foreign_keys == [1, 2, 3]

    def test_generate_value_returns_indexed_value(self):
        seed = OrderedForeignKeyModelFieldSeed(model_foreign_keys=[10, 20, 30])
        assert seed.generate_value(seed_index=0) == 10
        assert seed.generate_value(seed_index=1) == 20
        assert seed.generate_value(seed_index=2) == 30

    def test_generate_value_index_out_of_bounds_returns_last(self):
        seed = OrderedForeignKeyModelFieldSeed(model_foreign_keys=[1, 2])
        assert seed.generate_value(seed_index=99) == 2

    def test_generate_value_empty_list_returns_none(self):
        seed = OrderedForeignKeyModelFieldSeed(model_foreign_keys=[])
        assert seed.generate_value(seed_index=0) is None


class TestSeedContainer(TestCase):
    def test_getitem_returns_value(self):
        seed = Seed({'name': 'Test Task', 'status': TaskStatusChoices.NEW})
        assert seed['name'] == 'Test Task'
        assert seed['status'] == TaskStatusChoices.NEW

    def test_getitem_missing_key_raises(self):
        seed = Seed({'name': 'Test Task'})
        with pytest.raises(KeyError):
            _ = seed['missing']

    def test_setitem_sets_value(self):
        seed = Seed({'name': 'Original'})
        seed['name'] = 'Updated'
        assert seed['name'] == 'Updated'

    def test_setitem_new_key(self):
        seed = Seed({'name': 'Original'})
        seed['status'] = TaskStatusChoices.DONE
        assert seed['status'] == TaskStatusChoices.DONE

    def test_delitem_removes_key(self):
        seed = Seed({'name': 'Test', 'status': TaskStatusChoices.NEW})
        del seed['status']
        with pytest.raises(KeyError):
            _ = seed['status']

    def test_to_dict_returns_underlying_dict(self):
        data = {'name': 'Test', 'status': TaskStatusChoices.NEW, 'is_active': True}
        seed = Seed(data)
        assert seed.to_dict() == data
        assert seed.to_dict() is not data

    def test_repr_returns_dict_repr(self):
        data = {'name': 'Test'}
        seed = Seed(data)
        assert repr(seed) == repr(data)

    def test_equality_same_data(self):
        seed1 = Seed({'name': 'Test', 'status': TaskStatusChoices.NEW})
        seed2 = Seed({'name': 'Test', 'status': TaskStatusChoices.NEW})
        assert seed1 == seed2

    def test_inequality_different_data(self):
        seed1 = Seed({'name': 'Test A'})
        seed2 = Seed({'name': 'Test B'})
        assert seed1 != seed2
