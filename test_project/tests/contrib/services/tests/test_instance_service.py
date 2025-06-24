from django.test import TestCase

from test_project.apps.test_model.models import TestModel
from test_project.apps.test_model.tests.factories import create_test_model, create_test_model_child


class TestInstanceService(TestCase):
    def setUp(self):
        self.test_model = create_test_model()

    def test_valid_update_model_fields(self):
        data = {
            'first_name': 'John',
            'last_name': 'Smith'
        }

        created = self.test_model.services.save_model_obj(**data)
        self.assertEqual(self.test_model.first_name, 'John')
        self.assertEqual(self.test_model.last_name, 'Smith')
        self.assertFalse(created)

    def test_valid_create_model_fields(self):
        new_instance = TestModel()

        data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'favorite_number': 42,
            'weight_lbs': 400
        }

        created = new_instance.services.save_model_obj(**data)
        self.assertEqual(new_instance.first_name, 'John')
        self.assertEqual(new_instance.services.test_model.first_name, 'John')
        self.assertEqual(new_instance.last_name, 'Smith')
        self.assertEqual(new_instance.services.test_model.last_name, 'Smith')
        self.assertIsNotNone(self.test_model.id)
        self.assertTrue(created)

    def test_invalid_field_name(self):
        # Skips the field and saves the instance.
        data = {
            'invalid_field': 'test'
        }
        created = self.test_model.services.save_model_obj(**data)
        self.assertFalse(created)

    def test_foreign_key_id_aliases(self):
        test_model = create_test_model()
        child = create_test_model_child()

        data = {
            'parent_id': test_model.id,
        }

        created = child.services.save_model_obj(**data)
        self.assertEqual(child.parent_id, test_model.id)
        self.assertFalse(created)

    def test_obj_foreign_key_id_aliases(self):
        test_model = create_test_model()
        child = create_test_model_child()

        data = {
            'parent': test_model,
        }

        created = child.services.save_model_obj(**data)
        self.assertEqual(child.parent_id, test_model.id)
        self.assertFalse(created)
