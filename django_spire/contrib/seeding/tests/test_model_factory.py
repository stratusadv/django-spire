import pytest
from django.db import models
from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed
from django_spire.contrib.seeding.seed.factory.model_factory import ModelSeedFactory


class DummyModel(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    count = models.IntegerField()

    class Meta:
        app_label = 'contrib'


class TestModelSeedFactory(TestCase):
    def test_model_used_field_names_includes_all_fields(self):
        class ModelSeeder(Seeder):
            model_class = DummyModel
            cache_enabled = False
            fields_seeds = {
                'name': Seeder.static('Test'),
                'status': Seeder.static('active'),
                'count': Seeder.static(1),
            }

        seeder = ModelSeeder(count=1, verbose=False)
        factory = ModelSeedFactory(seeder=seeder)

        field_names = factory._model_used_field_names
        assert 'name' in field_names
        assert 'status' in field_names
        assert 'count' in field_names

    def test_model_all_field_names_includes_attnames(self):
        class ModelSeeder(Seeder):
            model_class = DummyModel
            cache_enabled = False
            fields_seeds = {
                'name': Seeder.static('Test'),
            }

        seeder = ModelSeeder(count=1, verbose=False)
        factory = ModelSeedFactory(seeder=seeder)

        field_names = factory._model_all_field_names
        assert len(field_names) > 0

    def test_validate_raises_on_invalid_field_name(self):
        class ModelSeeder(Seeder):
            model_class = DummyModel
            cache_enabled = False
            fields_seeds = {
                'invalid_field_name': Seeder.static('Test'),
            }

        seeder = ModelSeeder(count=1, verbose=False)

        with pytest.raises(ValueError, match='Invalid field name'):
            ModelSeedFactory(seeder=seeder)

    def test_validate_raises_on_multiple_invalid_fields(self):
        class ModelSeeder(Seeder):
            model_class = DummyModel
            cache_enabled = False
            fields_seeds = {
                'fake_field_1': Seeder.static('Test'),
                'fake_field_2': Seeder.static('Test'),
            }

        seeder = ModelSeeder(count=1, verbose=False)

        with pytest.raises(ValueError) as ctx:
            ModelSeedFactory(seeder=seeder)

        assert 'fake_field_1' in str(ctx.value)
        assert 'fake_field_2' in str(ctx.value)

    def test_validate_passes_with_all_valid_fields(self):
        class ModelSeeder(Seeder):
            model_class = DummyModel
            cache_enabled = False
            fields_seeds = {
                'name': Seeder.static('Test'),
                'status': Seeder.static('active'),
                'count': Seeder.static(1),
            }

        seeder = ModelSeeder(count=1, verbose=False)
        factory = ModelSeedFactory(seeder=seeder)
        assert factory is not None

    def test_generates_seeds_with_model_class(self):
        class ModelSeeder(Seeder):
            model_class = DummyModel
            cache_enabled = False
            fields_seeds = {
                'name': Seeder.static('Test'),
                'status': Seeder.static('active'),
                'count': Seeder.static(1),
            }

        seeder = ModelSeeder(count=2, verbose=False)
        factory = ModelSeedFactory(seeder=seeder)
        seeds = factory.generate_seeds(count=2, cache_enabled=False, cache_name='test_model_cache')

        assert len(seeds) == 2
        assert seeds[0]['name'] == 'Test'
        assert seeds[0]['status'] == 'active'
        assert seeds[0]['count'] == 1