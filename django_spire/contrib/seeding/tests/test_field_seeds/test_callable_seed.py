from django.test import TestCase

from django_spire.contrib.seeding.field.seed.callable_seed import CallableFieldSeed


class TestCallableFieldSeed(TestCase):
    def test_calls_function_with_no_wrapper(self):
        def get_value() -> str:
            return 'hello'

        seed = CallableFieldSeed(callable_=get_value)
        assert seed.generate_value(0) == 'hello'

    def test_with_wrapper_applies_wrapper(self):
        def uppercase(value):
            return value.upper()

        seed = CallableFieldSeed(callable_=lambda: 'hello', wrapper=uppercase)
        assert seed.generate_value(0) == 'HELLO'

    def test_wrapper_receives_callable_result(self):
        def add_exclamation(value):
            return f'{value}!'

        seed = CallableFieldSeed(callable_=lambda: 'hello', wrapper=add_exclamation)
        assert seed.generate_value(0) == 'hello!'

    def test_callable_returns_int(self):
        seed = CallableFieldSeed(callable_=lambda: 42)
        assert seed.generate_value(0) == 42

    def test_callable_without_kwargs(self):
        seed = CallableFieldSeed(callable_=lambda: 42)
        assert seed.generate_value(0) == 42

    def test_stores_callable_attribute(self):
        def my_callable():
            return 'result'

        seed = CallableFieldSeed(callable_=my_callable)
        assert seed.callable is my_callable

    def test_stores_wrapper_attribute(self):
        def wrapper(x):
            return x

        seed = CallableFieldSeed(callable_=lambda: 1, wrapper=wrapper)
        assert seed.wrapper is wrapper

    def test_stores_kwargs_attribute(self):
        seed = CallableFieldSeed(callable_=lambda: 'test')
        assert hasattr(seed, 'kwargs')

    def test_wrapper_none_returns_direct_result(self):
        seed = CallableFieldSeed(callable_=lambda: 'direct', wrapper=None)
        assert seed.generate_value(0) == 'direct'

    def test_with_complex_wrapper(self):
        def double_and_capitalize(value):
            return value.upper() + value.upper()

        seed = CallableFieldSeed(callable_=lambda: 'test', wrapper=double_and_capitalize)
        assert seed.generate_value(0) == 'TESTTEST'

    def test_lambda_returns_value(self):
        seed = CallableFieldSeed(callable_=lambda: 'lambda_result')
        assert seed.generate_value(0) == 'lambda_result'