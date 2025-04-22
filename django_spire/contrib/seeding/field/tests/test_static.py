import unittest
from django_spire.contrib.seeding.field.static import StaticFieldSeeder


class TestStaticFieldSeeder(unittest.TestCase):

    def test_seeds_static_fields(self):
        fields = {
            "category": ("static", "books"),
            "in_stock": ("static", True)
        }
        seeder = StaticFieldSeeder(fields=fields)
        result = seeder.seed(count=3)

        self.assertEqual(len(result), 3)
        for row in result:
            self.assertEqual(row["category"], "books")
            self.assertEqual(row["in_stock"], True)
