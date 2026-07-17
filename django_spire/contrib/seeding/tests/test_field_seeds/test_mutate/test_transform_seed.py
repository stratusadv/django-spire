from django.test import TestCase

from django_spire.contrib.seeding.field.seed.mutate.transform_seed import TransformMutateFieldSeed
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed


class TestTransformMutateFieldSeed(TestCase):
    def test_init_stores_field_seed(self):
        wrapped = StaticFieldSeed('hello')
        seed = TransformMutateFieldSeed(field_seed=wrapped, transform=str.upper, change_chance=0.5)
        assert seed.field_seed is wrapped

    def test_init_stores_transform(self):
        wrapped = StaticFieldSeed('hello')
        seed = TransformMutateFieldSeed(field_seed=wrapped, transform=str.upper, change_chance=0.5)
        assert seed.transform is str.upper

    def test_init_stores_change_chance(self):
        wrapped = StaticFieldSeed('value')
        seed = TransformMutateFieldSeed(field_seed=wrapped, transform=str.upper, change_chance=0.8)
        assert seed.change_chance == 0.8

    def test_default_change_chance(self):
        wrapped = StaticFieldSeed('value')
        seed = TransformMutateFieldSeed(field_seed=wrapped, transform=str.upper)
        assert seed.change_chance == 0.5

    def test_generate_value_applies_transform(self):
        wrapped = StaticFieldSeed('hello world')
        seed = TransformMutateFieldSeed(
            field_seed=wrapped, transform=lambda v: v.upper(), change_chance=1.0
        )
        assert seed.generate_value(0) == 'HELLO WORLD'

    def test_generate_value_handles_none(self):
        wrapped = StaticFieldSeed(None)
        seed = TransformMutateFieldSeed(
            field_seed=wrapped,
            transform=lambda v: v.upper() if v else 'DEFAULT',
            change_chance=1.0,
        )
        assert seed.generate_value(0) == 'DEFAULT'

    def test_zero_change_chance_returns_original(self):
        wrapped = StaticFieldSeed('original')
        seed = TransformMutateFieldSeed(field_seed=wrapped, transform=str.upper, change_chance=0.0)
        for _ in range(10):
            assert seed.generate_value(0) == 'original'

    def test_one_change_chance_always_transforms(self):
        wrapped = StaticFieldSeed('hello')
        seed = TransformMutateFieldSeed(field_seed=wrapped, transform=str.upper, change_chance=1.0)
        for _ in range(10):
            assert seed.generate_value(0) == 'HELLO'

    def test_generate_value_passes_seed_index(self):
        wrapped = StaticFieldSeed('value')
        seed = TransformMutateFieldSeed(
            field_seed=wrapped, transform=lambda v: f'{v}_{v}', change_chance=1.0
        )
        for idx in range(3):
            result = seed.generate_value(idx)
            assert 'value' in result

    def test_lambda_transform(self):
        wrapped = StaticFieldSeed(5)
        seed = TransformMutateFieldSeed(
            field_seed=wrapped, transform=lambda v: v * 2, change_chance=1.0
        )
        assert seed.generate_value(0) == 10

    def test_complex_transform(self):
        wrapped = StaticFieldSeed('hello world')
        seed = TransformMutateFieldSeed(
            field_seed=wrapped,
            transform=lambda v: ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(v)),
            change_chance=1.0,
        )
        assert seed.generate_value(0) == 'HeLlO WoRlD'