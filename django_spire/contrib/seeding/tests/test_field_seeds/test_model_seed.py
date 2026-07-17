from django.test import TestCase

from django_spire.contrib.seeding.field.seed.model_seed import OrderedForeignKeyModelFieldSeed


class TestOrderedForeignKeyModelFieldSeed(TestCase):
    def test_init_stores_queryset(self):
        seed = OrderedForeignKeyModelFieldSeed(queryset=None)
        assert seed is not None

    def test_model_foreign_keys_class_attribute_starts_none(self):
        assert OrderedForeignKeyModelFieldSeed.model_foreign_keys is None