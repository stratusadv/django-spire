import unittest
from django_spire.contrib.seeding.field.base import BaseFieldSeeder


class DummyFieldSeeder(BaseFieldSeeder):
    keyword = "faker"

    def seed(self, model_seeder_cls=None, count: int = 1):
        return [{"fake": True} for _ in range(count)]


class TestBaseFieldSeeder(unittest.TestCase):

    def test_filter_fields(self):
        fields = {
            "name": ("faker", "name"),
            "email": ("faker", "email"),
            "description": ("llm", "prompt")
        }
        seeder = DummyFieldSeeder(fields=fields)
        faker_fields = seeder.filter_fields("faker")
        self.assertIn("name", faker_fields)
        self.assertIn("email", faker_fields)
        self.assertNotIn("description", faker_fields)
