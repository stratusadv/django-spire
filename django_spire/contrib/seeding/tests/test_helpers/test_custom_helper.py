import random

from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed


class TestCustomFieldSeedHelper(TestCase):
    def test_callable_wraps_function(self):
        def get_value():
            return 42

        seed = Seeder.custom.callable(get_value)
        assert isinstance(seed, CallableFieldSeed)
        assert seed.generate_value(0) == 42

    def test_callable_with_args(self):
        def add(a, b):
            return a + b

        seed = Seeder.custom.callable(add, a=5, b=7)
        assert seed.generate_value(0) == 12

    def test_callable_with_custom_func(self):
        def random_boolean(true_weight=0.5):
            return random.random() <= true_weight

        seed = Seeder.custom.callable(random_boolean, true_weight=1.0)
        assert seed.generate_value(0) is True

    def test_lambda_callable(self):
        seed = Seeder.custom.callable(lambda: 'lambda_result')
        assert seed.generate_value(0) == 'lambda_result'

    def test_callable_with_no_args(self):
        def constant_value():
            return 'constant'

        seed = Seeder.custom.callable(constant_value)
        assert seed.generate_value(0) == 'constant'
        assert seed.generate_value(1) == 'constant'

    def test_callable_returns_list(self):
        def get_list():
            return [1, 2, 3]

        seed = Seeder.custom.callable(get_list)
        assert seed.generate_value(0) == [1, 2, 3]

    def test_callable_with_no_args(self):
        def constant_value():
            return 'constant'

        seed = Seeder.custom.callable(constant_value)
        assert seed.generate_value(0) == 'constant'
        assert seed.generate_value(1) == 'constant'

    def test_callable_returns_none(self):
        def return_none():
            return None

        seed = Seeder.custom.callable(return_none)
        assert seed.generate_value(0) is None

    def test_callable_with_complex_logic(self):
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n - 1) + fibonacci(n - 2)

        seed = Seeder.custom.callable(fibonacci, n=10)
        assert seed.generate_value(0) == 55