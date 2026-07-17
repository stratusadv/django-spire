import pytest
from django.test import TestCase

from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed
from django_spire.contrib.seeding.seed.seed import Seed


class TestSeederDatabaseRequiresModel(TestCase):
    def test_seed_database_requires_model_class(self):
        class NoModelSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = NoModelSeeder(count=1, verbose=False)
        with pytest.raises(DjangoSpireSeederError) as ctx:
            seeder.seed_database()

        assert 'Cannot seed database without a model class' in str(ctx.value)

    def test_to_model_instances_requires_model_class(self):
        class NoModelSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = NoModelSeeder(count=1, verbose=False)
        seeder.seed()

        with pytest.raises(DjangoSpireSeederError) as ctx:
            seeder.to_model_instances()

        assert 'Cannot create models instances without a model class' in str(ctx.value)

    def test_queryset_property_requires_model_class(self):
        class NoModelSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {'name': StaticFieldSeed('Test')}

        seeder = NoModelSeeder(count=1, verbose=False)
        seeder.seeds = []
        seeder._model_object_ids = []

        with pytest.raises(DjangoSpireSeederError) as ctx:
            _ = seeder.queryset

        assert 'Cannot create queryset without a model class' in str(ctx.value)


class TestSeederDatabaseWithModel(TestCase):
    def test_to_model_instances_raises_without_model_class(self):
        class ModelSeeder(Seeder):
            model_class = None
            cache_enabled = False
            fields_seeds = {
                'name': StaticFieldSeed('Test'),
            }

        seeder = ModelSeeder(count=1, verbose=False)
        seeder.seeds = [Seed({'name': 'Test'})]
        with pytest.raises(DjangoSpireSeederError, match='Cannot create models instances'):
            seeder.to_model_instances()