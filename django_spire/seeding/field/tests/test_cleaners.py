import unittest
from copy import copy
from django_spire.seeding.field.cleaners import normalize_seeder_fields


FIELDS = {
    "faker_tuple": ("faker", "name"),
    "llm_type": "llm",
    "faker_type": "faker",
    "static_type": "static",
    "callable_type": "callable",
    "custom_type": "custom",
    "static_bool": True,
    "static_str": "approved",
    "static_int": 10,
    "callable_func": lambda: "now",
    "exclude_str": "exclude",
    "exclude_tuple": ("exclude",)
}


class TestNormalizeSeederFields(unittest.TestCase):

    def test_normalizes_faker_tuple(self):
        fields = {"faker_tuple": FIELDS["faker_tuple"]}
        normalized = normalize_seeder_fields(fields)
        self.assertEqual(normalized["faker_tuple"], ("faker", "name"))

    def test_excludes_fields(self):
        fields = copy(FIELDS)
        normalized = normalize_seeder_fields(fields)
        self.assertNotIn("exclude_str", normalized)
        self.assertNotIn("exclude_tuple", normalized)
        self.assertIn("static_str", normalized)

    def test_normalizes_single_value_strings_to_tuples(self):
        fields = {
            k: FIELDS[k] for k in (
                "llm_type", "faker_type", "static_type", "callable_type", "custom_type"
            )
        }
        normalized = normalize_seeder_fields(fields)
        for key, value in fields.items():
            self.assertEqual(normalized[key], (value,))

    def test_normalizes_callable(self):
        fields = {"callable_func": FIELDS["callable_func"]}
        normalized = normalize_seeder_fields(fields)
        self.assertEqual(normalized["callable_func"][0], "callable")
        self.assertTrue(callable(normalized["callable_func"][1]))

    def test_normalizes_static_values(self):
        fields = {
            "static_bool": FIELDS["static_bool"],
            "static_str": FIELDS["static_str"],
            "static_int": FIELDS["static_int"]
        }
        normalized = normalize_seeder_fields(fields)
        self.assertEqual(normalized["static_bool"], ("static", True))
        self.assertEqual(normalized["static_str"], ("static", "approved"))
        self.assertEqual(normalized["static_int"], ("static", 10))
