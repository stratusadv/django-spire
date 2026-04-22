from __future__ import annotations

from django.test import TestCase

from test_project.apps.model_and_service.models import Adult
from test_project.apps.model_and_service.tests.factories import create_adult, create_kid


class TestInstanceService(TestCase):
    def setUp(self):
        self.adult = create_adult()

    def test_valid_update_model_fields(self):
        data = {
            'first_name': 'John',
            'last_name': 'Smith'
        }

        self.adult, created = self.adult.services.save_model_obj(**data)
        assert self.adult.first_name == 'John'
        assert self.adult.last_name == 'Smith'
        assert not created

    def test_valid_create_model_fields(self):
        new_adult = Adult()

        data = {
            'first_name': 'John',
            'last_name': 'Smith',
            'favorite_number': 42,
            'weight_lbs': 400
        }

        new_adult, created = new_adult.services.save_model_obj(**data)
        assert new_adult.first_name == 'John'
        assert new_adult.services.obj.first_name == 'John'
        assert new_adult.last_name == 'Smith'
        assert new_adult.services.obj.last_name == 'Smith'
        assert self.adult.id is not None
        assert created

    def test_invalid_field_name(self):
        # Skips the field and saves the instance.
        data = {
            'invalid_field': 'test'
        }
        self.adult, created = self.adult.services.save_model_obj(**data)
        assert not created

    def test_foreign_key_id_aliases(self):
        new_adult = create_adult()
        new_kid = create_kid()

        data = {
            'parent_id': new_adult.id,
        }

        new_kid, created = new_kid.services.save_model_obj(**data)
        assert new_kid.parent_id == new_adult.id
        assert not created

    def test_obj_foreign_key_id_aliases(self):
        new_adult = create_adult()
        new_kid = create_kid()

        data = {
            'parent': new_adult,
        }

        new_kid, created = new_kid.services.save_model_obj(**data)
        assert new_kid.parent_id == new_adult.id
        assert not created

    def test_sub_service_depth(self):
        new_adult = create_adult()
        new_kid = create_kid()

        data = {
            'parent': new_adult,
        }

        new_kid, created = new_kid.services.save_model_obj(**data)

        assert new_kid.parent_id == new_adult.id
        assert new_kid.services.obj.parent_id == new_adult.id
        assert new_kid.services.sub.obj.parent_id == new_adult.id
        assert new_kid.services.sub.deep.obj.parent_id == new_adult.id

        new_kid.first_name = 'George'
        assert new_kid.services.sub.deep.obj.first_name == 'George'

        new_kid.services.sub.deep.obj.first_name = 'Burt'

        assert new_kid.first_name == 'Burt'
        assert not created
