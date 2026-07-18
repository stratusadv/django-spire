from django.test import TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.seeding.field.seed.model_seed import (
    BaseForeignKeyModelFieldSeed,
    OrderedForeignKeyModelFieldSeed,
    RandomForeignKeyModelFieldSeed,
)


class TestOrderedForeignKeyModelFieldSeed(TestCase):
    def setUp(self):
        BaseForeignKeyModelFieldSeed._model_foreign_keys.clear()
        self.user_one = AuthUser.objects.create(username='user_one')
        self.user_two = AuthUser.objects.create(username='user_two')
        self.queryset = AuthUser.objects.order_by('pk')

    def test_init_stores_queryset(self):
        seed = OrderedForeignKeyModelFieldSeed(queryset=self.queryset)
        assert seed.queryset is self.queryset
        assert seed.queryset_key == str(self.queryset.query)

    def test_model_foreign_keys_caches_ids_by_queryset_key(self):
        seed = OrderedForeignKeyModelFieldSeed(queryset=self.queryset)
        assert seed.model_foreign_keys(0) == [self.user_one.pk, self.user_two.pk]
        cache = BaseForeignKeyModelFieldSeed._model_foreign_keys
        assert cache[seed.queryset_key] == [self.user_one.pk, self.user_two.pk]

    def test_model_foreign_keys_refreshes_on_seed_index_zero(self):
        seed = OrderedForeignKeyModelFieldSeed(queryset=self.queryset)
        seed.model_foreign_keys(0)
        user_three = AuthUser.objects.create(username='user_three')
        assert user_three.pk not in seed.model_foreign_keys(1)
        assert user_three.pk in seed.model_foreign_keys(0)

    def test_generate_value_returns_ids_in_order(self):
        seed = OrderedForeignKeyModelFieldSeed(queryset=self.queryset)
        assert seed.generate_value(0) == self.user_one.pk
        assert seed.generate_value(1) == self.user_two.pk


class TestRandomForeignKeyModelFieldSeed(TestCase):
    def setUp(self):
        BaseForeignKeyModelFieldSeed._model_foreign_keys.clear()
        self.user_one = AuthUser.objects.create(username='user_one')
        self.user_two = AuthUser.objects.create(username='user_two')
        self.queryset = AuthUser.objects.order_by('pk')

    def test_generate_value_returns_id_from_queryset(self):
        seed = RandomForeignKeyModelFieldSeed(queryset=self.queryset)
        for seed_index in range(10):
            assert seed.generate_value(seed_index) in [self.user_one.pk, self.user_two.pk]
