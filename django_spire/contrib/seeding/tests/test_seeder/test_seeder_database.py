import json
import pytest
from django.db import models
from django.test import TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.seeding import Seeder
from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError
from django_spire.contrib.seeding.field.seed.static_seed import StaticFieldSeed
from django_spire.contrib.seeding.seed.seed import Seed


class SimpleRow(models.Model):
    name = models.CharField(max_length=100)
    count = models.IntegerField()

    class Meta:
        app_label = 'contrib'

    def __str__(self) -> str:
        return self.name


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


class AuthUserSeeder(Seeder):
    model_class = AuthUser
    cache_enabled = False
    fields_seeds = {
        'username': Seeder.fake.uuid4(),
        'first_name': Seeder.static('Seeded'),
        'last_name': Seeder.static('User'),
        'email': Seeder.fake.email(),
        'is_active': Seeder.static(True),
    }


class TestSeederSeedDatabase(TestCase):
    def _auth_user_seeder(self, count):
        class AuthUserSeeder(Seeder):
            model_class = AuthUser
            cache_enabled = False
            fields_seeds = {
                'username': Seeder.fake.uuid4(),
                'first_name': Seeder.static('Seeded'),
                'last_name': Seeder.static('User'),
                'email': Seeder.fake.email(),
                'is_active': Seeder.static(True),
            }

        return AuthUserSeeder(count=count, verbose=False)

    def test_seed_database_returns_queryset_of_created_rows(self):
        seeder = self._auth_user_seeder(3)
        queryset = seeder.seed_database()
        assert queryset.count() == 3
        assert len(set(queryset.values_list('username', flat=True))) == 3

    def test_seed_database_persists_static_fields(self):
        seeder = self._auth_user_seeder(2)
        seeder.seed_database()
        for user in seeder.queryset:
            assert user.first_name == 'Seeded'
            assert user.last_name == 'User'
            assert user.is_active is True

    def test_seed_database_records_model_object_ids(self):
        seeder = self._auth_user_seeder(2)
        seeder.seed_database()
        assert len(seeder._model_object_ids) == 2
        assert sorted(seeder._model_object_ids) == sorted(
            AuthUser.objects.values_list('id', flat=True)
        )

    def test_seed_database_with_override_count(self):
        seeder = self._auth_user_seeder(2)
        assert seeder.seed_database(count=4).count() == 4

    def test_seed_database_does_not_regenerate_existing_seeds(self):
        seeder = self._auth_user_seeder(2)
        seeder.seed_database()
        original = [seed.to_dict() for seed in seeder.seeds]
        seeder.seed()
        assert [seed.to_dict() for seed in seeder.seeds] == original

    def test_queryset_only_returns_seeded_rows(self):
        AuthUser.objects.create(username='pre_existing')
        seeder = self._auth_user_seeder(2)
        seeder.seed_database()
        usernames = set(seeder.queryset.values_list('username', flat=True))
        assert 'pre_existing' not in usernames
        assert len(usernames) == 2

    def test_post_seed_database_hook_runs(self):
        class HookSeeder(Seeder):
            model_class = AuthUser
            cache_enabled = False
            hook_calls = 0
            fields_seeds = {'username': Seeder.fake.uuid4()}

            def __post_seed_database__(self):
                type(self).hook_calls += 1

        HookSeeder(count=1, verbose=False).seed_database()
        assert HookSeeder.hook_calls == 1

    def test_to_model_instances_are_unsaved_before_seed_database(self):
        seeder = self._auth_user_seeder(2)
        instances = seeder.to_model_instances()
        assert len(instances) == 2
        assert all(isinstance(instance, AuthUser) for instance in instances)
        assert all(instance.pk is None for instance in instances)
        assert AuthUser.objects.count() == 0

    def test_to_json_serializes_saved_queryset(self):
        seeder = self._auth_user_seeder(2)
        seeder.seed_database()
        payload = json.loads(seeder.to_json())
        assert len(payload) == 2
        assert all(record['pk'] in seeder._model_object_ids for record in payload)

    def test_to_json_serializes_unsaved_instances(self):
        class RowSeeder(Seeder):
            model_class = SimpleRow
            cache_enabled = False
            fields_seeds = {
                'name': Seeder.static('Seeded'),
                'count': Seeder.static(7),
            }

        payload = json.loads(RowSeeder(count=2, verbose=False).to_json())
        assert len(payload) == 2
        assert payload[0]['fields']['name'] == 'Seeded'
        assert payload[0]['fields']['count'] == 7

    def test_to_json_of_unsaved_instances_fails_on_many_to_many_model(self):
        seeder = self._auth_user_seeder(2)
        with pytest.raises(ValueError, match='before this many-to-many relationship'):
            seeder.to_json()

    def test_reset_clears_tracked_ids_but_keeps_rows(self):
        seeder = self._auth_user_seeder(2)
        seeder.seed_database()
        seeder.reset()
        assert seeder._model_object_ids == []
        assert seeder.seeds == []
        assert AuthUser.objects.count() == 2

    def test_seed_class_builds_plain_objects(self):
        class Row:
            def __init__(self, username, first_name, last_name, email, is_active):
                self.username = username
                self.first_name = first_name
                self.last_name = last_name
                self.email = email
                self.is_active = is_active

        rows = self._auth_user_seeder(2).seed_class(Row)
        assert len(rows) == 2
        assert all(isinstance(row, Row) for row in rows)
        assert all(row.first_name == 'Seeded' for row in rows)


class TestSeederReseedDatabase(TestCase):
    def _auth_user_seeder(self, count):
        class AuthUserSeeder(Seeder):
            model_class = AuthUser
            cache_enabled = False
            fields_seeds = {'username': Seeder.fake.uuid4()}

        return AuthUserSeeder(count=count, verbose=False)

    def test_reseed_database_creates_a_second_batch(self):
        seeder = self._auth_user_seeder(2)
        first_ids = list(seeder.seed_database().values_list('id', flat=True))
        second_ids = list(seeder.reseed_database().values_list('id', flat=True))
        assert set(first_ids).isdisjoint(second_ids)
        assert AuthUser.objects.count() == 4

    def test_reseed_database_replaces_tracked_object_ids(self):
        seeder = self._auth_user_seeder(2)
        seeder.seed_database()
        first_ids = list(seeder._model_object_ids)
        seeder.reseed_database()
        assert seeder._model_object_ids != first_ids
        assert len(seeder._model_object_ids) == 2
