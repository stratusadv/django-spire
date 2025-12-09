from __future__ import annotations

import pytest

from django.db import models
from django.test import TestCase
from django.utils.timezone import now

from django_spire.contrib.seeding import DjangoModelSeeder


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    sku = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'tests'
        managed = False

    def __str__(self) -> str:
        return 'Product'


class ProductSeeder(DjangoModelSeeder):
    model_class = Product
    fields = {
        'name': ('llm', 'Clothing store'),
        'description': ('static', 'A great product for testing.'),
        'price': ('faker', 'pydecimal', {'left_digits': 2, 'right_digits': 2, 'positive': True}),
        'in_stock': True,
        'created_at': ('callable', now),
        'updated_at': 'exclude',
    }


class TestProductSeeder(TestCase):
    def test_assign_defaults(self) -> None:
        assert 'sku' in ProductSeeder.resolved_fields()

    def test_field_override_applies(self) -> None:
        override_time = now()

        result = ProductSeeder.seed(count=1, fields={'updated_at': ('static', override_time)})

        assert result[0].updated_at == override_time

    def test_raises_for_invalid_field(self) -> None:
        with pytest.raises(Exception) as exc_info:
            ProductSeeder.seed(count=1, fields={'not_a_field': ('static', 'value')})

        assert 'not_a_field' in str(exc_info.value)

    def test_seeds_three_objects(self) -> None:
        result = ProductSeeder.seed(count=3)

        assert len(result) == 3

        for obj in result:
            assert isinstance(obj, Product)
