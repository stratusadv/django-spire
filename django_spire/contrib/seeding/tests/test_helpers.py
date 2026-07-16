import random

from django.test import TestCase
from django.utils import timezone

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed
from django_spire.contrib.seeding.field.seed.exclude_seed import ExcludeFieldSeed
from django_spire.contrib.seeding.field.seed.llm_seed import LlmFieldSeed
from django_spire.contrib.seeding.field.seed.random_seed import RandomFieldSeed as RandomSeed

from test_project.app.task.choices import TaskStatusChoices


class TestFakeFieldSeedHelper(TestCase):
    def test_first_name_returns_callable_field_seed(self):
        seed = Seeder.fake.first_name()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.first_name
        assert seed.kwargs == {}

    def test_last_name_returns_callable_field_seed(self):
        seed = Seeder.fake.last_name()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.last_name

    def test_sentence_default_nb_words(self):
        seed = Seeder.fake.sentence()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.sentence
        assert seed.kwargs == {'nb_words': 5}

    def test_sentence_custom_nb_words(self):
        seed = Seeder.fake.sentence(nb_words=10)
        assert seed.kwargs == {'nb_words': 10}

    def test_boolean_returns_callable_field_seed(self):
        seed = Seeder.fake.boolean()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.boolean

    def test_date_between_returns_callable_with_make_aware(self):
        seed = Seeder.fake.date_between()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.date_between
        assert seed.wrapper is timezone.make_aware

    def test_date_time_between_returns_callable_with_make_aware(self):
        seed = Seeder.fake.date_time_between()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.date_time_between
        assert seed.wrapper is timezone.make_aware

    def test_date_time_between_returns_aware_datetime(self):
        seed = Seeder.fake.date_time_between()
        value = seed.generate_value()
        assert timezone.is_aware(value)

    def test_text_returns_callable_field_seed(self):
        seed = Seeder.fake.text()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.fake.faker.text
        assert seed.kwargs == {'max_nb_chars': 200}

    def test_text_custom_max_chars(self):
        seed = Seeder.fake.text(max_nb_chars=100)
        assert seed.kwargs == {'max_nb_chars': 100}

    def test_provider_valid_method(self):
        seed = Seeder.fake.provider('name')
        assert isinstance(seed, CallableFieldSeed)
        assert seed.kwargs == {}

    def test_provider_with_kwargs(self):
        seed = Seeder.fake.provider('random_int', min=1, max=10)
        assert seed.kwargs == {'min': 1, 'max': 10}


class TestCustomFieldSeedHelper(TestCase):
    def test_callable_wraps_function(self):
        def get_value() -> int:
            return 42

        seed = Seeder.custom.callable(get_value)
        assert isinstance(seed, CallableFieldSeed)
        assert seed.generate_value() == 42

    def test_callable_with_args(self):
        def add(a: int, b: int) -> int:
            return a + b

        seed = Seeder.custom.callable(add, a=5, b=7)
        assert seed.generate_value() == 12

    def test_callable_with_custom_func(self):
        def random_boolean(true_weight: float = 0.5) -> bool:
            return random.random() <= true_weight

        seed = Seeder.custom.callable(random_boolean, true_weight=1.0)
        assert seed.generate_value() is True


class TestModelFieldSeedHelper(TestCase):
    def test_random_field_choice_returns_random_field_seed(self):
        seed = Seeder.model.random_field_choice(TaskStatusChoices)
        assert isinstance(seed, RandomSeed)
        assert seed.enum_ is TaskStatusChoices

    def test_random_foreign_key_returns_callable_field_seed(self):
        seed = Seeder.model.random_foreign_key(TaskStatusChoices)
        assert isinstance(seed, CallableFieldSeed)


class TestRandomFieldSeedHelper(TestCase):
    def test_choice_returns_callable_field_seed(self):
        seq = ['a', 'b', 'c']
        seed = Seeder.random.choice(seq)
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.random.faker.random.choice
        assert seed.kwargs == {'seq': seq}

    def test_choice_generates_from_sequence(self):
        seq = [1, 2, 3]
        seed = Seeder.random.choice(seq)
        value = seed.generate_value()
        assert value in seq

    def test_enum_returns_random_field_seed(self):
        seed = Seeder.random.enum(TaskStatusChoices)
        assert isinstance(seed, RandomSeed)
        assert seed.enum_ is TaskStatusChoices

    def test_enum_generates_enum_value(self):
        seed = Seeder.random.enum(TaskStatusChoices)
        value = seed.generate_value()
        assert value in list(TaskStatusChoices)

    def test_float_default_range(self):
        seed = Seeder.random.float()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.random.faker.random.uniform
        assert seed.kwargs == {'a': 0.0, 'b': 1.0}

    def test_float_custom_range(self):
        seed = Seeder.random.float(a=5.0, b=10.0)
        value = seed.generate_value()
        assert 5.0 <= value <= 10.0

    def test_int_default_range(self):
        seed = Seeder.random.int()
        assert isinstance(seed, CallableFieldSeed)
        assert seed.callable is Seeder.random.faker.random.randint
        assert seed.kwargs == {'a': 0, 'b': 100}

    def test_int_custom_range(self):
        seed = Seeder.random.int(a=10, b=20)
        value = seed.generate_value()
        assert 10 <= value <= 20


class TestSeederStaticMethods(TestCase):
    def test_exclude_returns_exclude_field_seed(self):
        seed = Seeder.exclude()
        assert isinstance(seed, ExcludeFieldSeed)

    def test_static_with_value(self):
        seed = Seeder.static('hello')
        assert isinstance(seed, CallableFieldSeed)
        assert seed.generate_value() == 'hello'

    def test_static_with_int(self):
        seed = Seeder.static(42)
        assert seed.generate_value() == 42

    def test_static_with_bool(self):
        seed = Seeder.static(value=True)
        assert seed.generate_value() is True

    def test_llm_returns_llm_field_seed(self):
        seed = Seeder.llm(str)
        assert isinstance(seed, LlmFieldSeed)
        assert seed.field_type is str
        assert seed.prompt is None

    def test_llm_with_prompt(self):
        seed = Seeder.llm(str, 'A task name')
        assert isinstance(seed, LlmFieldSeed)
        assert seed.prompt == 'A task name'

    def test_llm_inherits_locale(self):
        class CustomSeeder(Seeder):
            locale = 'en_US'

        seed = CustomSeeder.llm(str)
        assert isinstance(seed, LlmFieldSeed)
        assert seed.locale == 'en_US'
