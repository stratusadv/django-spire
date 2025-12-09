from __future__ import annotations

from django_spire.contrib.seeding import DjangoModelSeeder
from django_spire.contrib.seeding.model.django.tests.test_seeder import Product


class ProductSeeder(DjangoModelSeeder):
    model_class = Product

    fields = {
        'id': 'exclude',
        'name': ('llm', 'Shirts for a upper end mens clothing store'),
        'sku': 'llm',
        'description': 'llm',
        'price': ('faker', 'pydecimal', {'left_digits': 2, 'right_digits': 2, 'positive': True}),
        'in_stock': True,
        'created_at': ('custom', 'date_time_between', {'start_date': '-30d', 'end_date': 'now'}),
        'updated_at': 'exclude',
    }
