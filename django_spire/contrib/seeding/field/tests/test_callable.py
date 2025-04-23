import unittest
from django_spire.contrib.seeding.field.callable import CallableFieldSeeder


class TestCallableFieldSeeder(unittest.TestCase):

    def test_seeds_callable_fields(self):
        fields = {
            "timestamp": lambda: "2024-01-01 12:00:00",
            "status": lambda: "active"
        }
        seeder = CallableFieldSeeder(fields=fields)
        result = seeder.seed(None, count=3)

        self.assertEqual(len(result), 3)
        for row in result:
            self.assertEqual(row["timestamp"], "2024-01-01 12:00:00")
            self.assertEqual(row["status"], "active")
