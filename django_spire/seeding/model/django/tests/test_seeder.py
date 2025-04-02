import unittest
from django.db import models
from django.utils.timezone import now

from django_spire.seeding import DjangoModelSeeder


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    sku = models.CharField(max_length=20, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "tests"
        managed = False


class ProductSeeder(DjangoModelSeeder):
    model_class = Product
    fields = {
        "name": ('llm', 'Clothing store'),
        "description": ('static', 'A great product for testing.'),
        "price": ('faker', 'pydecimal', {'left_digits': 2, 'right_digits': 2, 'positive': True}),
        "in_stock": True,
        "created_at": ("callable", now),
        "updated_at": 'exclude',
    }


class TestProductSeeder(unittest.TestCase):

    def test_assign_defaults(self):
        self.assertIn('sku', ProductSeeder.fields)

    def test_seeds_three_objects(self):
        result = ProductSeeder.seed(count=3)
        self.assertEqual(len(result), 3)
        for obj in result:
            self.assertIsInstance(obj, Product)

    def test_raises_for_invalid_field(self):
        with self.assertRaises(Exception) as context:
            ProductSeeder.seed(count=1, fields={"not_a_field": ("static", "value")})
        self.assertIn("not_a_field", str(context.exception))

    def test_field_override_applies(self):
        override_time = now()
        result = ProductSeeder.seed(count=1, fields={"updated_at": ("static", override_time)})
        self.assertEqual(result[0].updated_at, override_time)
