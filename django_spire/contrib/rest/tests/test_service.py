from __future__ import annotations

import pytest

from django.contrib.auth.models import User
from django.test import TestCase

from django_spire.contrib.rest.service import BaseRestService
from django_spire.contrib.rest.tests.example_users import (
    DummyJsonUserClient,
    UserSchema, UserRestService, UserRestServiceWithMapping,
)


class TestBaseRestService(TestCase):
    def test_model_to_schema_custom(self):
        # Create Django User instance
        user = User(
            id=1,
            first_name="Emily",
            last_name="Johnson",
            email="emily.johnson@example.com",
            username="emilys"
        )

        service = UserRestService(user)

        # Convert to schema using custom implementation
        schema = service.model_to_schema(user)

        assert isinstance(schema, UserSchema)
        assert schema.id == 1
        assert schema.firstName == "Emily"
        assert schema.lastName == "Johnson"
        assert schema.email == "emily.johnson@example.com"
        assert schema.username == "emilys"

    def test_schema_to_model_new(self):
        # Fetch real user data from API
        client = DummyJsonUserClient()
        schema = client.fetch_one(1)

        temp_user = User(id=999, username="temp")
        service = UserRestService(temp_user)

        # Convert to new model instance
        new_user = service.schema_to_model(schema)

        assert isinstance(new_user, User)
        assert new_user.id == schema.id
        assert new_user.first_name == schema.firstName
        assert new_user.last_name == schema.lastName
        assert new_user.email == schema.email
        assert new_user.username == schema.username

    def test_schema_to_model_update_existing(self):
        # Create existing user with old data
        user = User(id=999, first_name="Old", last_name="Name", email="old@example.com", username="olduser")

        # Fetch real data from API
        client = DummyJsonUserClient()
        schema = client.fetch_one(1)

        service = UserRestService(user)

        # Update existing model
        updated_user = service.schema_to_model(schema, user)

        assert updated_user is user  # Same instance
        assert user.id == 1
        assert user.first_name == "Emily"
        assert user.last_name == "Johnson"
        assert user.username == "emilys"

    def test_get_identifier(self):
        user = User(id=25, username="testuser")

        service = UserRestService(user)
        identifier = service.get_identifier(user)

        assert identifier == "25"

    def test_service_client_access(self):
        user = User(id=1, username="test")
        service = UserRestService(user)

        client = service.client

        assert isinstance(client, DummyJsonUserClient)
        assert client.base_url == 'https://dummyjson.com'
        assert client.base_path == 'users'

    def test_service_requires_client(self):
        with pytest.raises(TypeError, match="must define a 'client' class attribute"):
            class InvalidService(BaseRestService[User, UserSchema, DummyJsonUserClient]):
                obj: User
                # Missing: client = DummyJsonUserClient()

    def test_valid_service_does_not_raise(self):
        # Should not raise
        class ValidService(BaseRestService[User, UserSchema, DummyJsonUserClient]):
            obj: User
            client = DummyJsonUserClient()

            def model_to_schema(self, model: User) -> UserSchema:
                return UserSchema(
                    id=model.id or 1,
                    firstName=model.first_name,
                    lastName=model.last_name,
                    email=model.email,
                    username=model.username,
                )

            def schema_to_model(self, schema: UserSchema, model: User | None = None) -> User:
                if model is None:
                    model = User()
                model.id = schema.id
                model.first_name = schema.firstName
                model.last_name = schema.lastName
                model.email = schema.email
                model.username = schema.username
                return model

        # Instantiate to verify it works
        user = User(id=1, username="test")
        service = ValidService(user)
        assert service.obj is user

    def test_conversion_round_trip(self):
        # Create Django User
        original = User(
            id=1,
            first_name="Emily",
            last_name="Johnson",
            email="emily.johnson@example.com",
            username="emilys"
        )
        service = UserRestService(original)

        # Convert to schema
        schema = service.model_to_schema(original)
        assert schema.id == 1
        assert schema.firstName == "Emily"
        assert schema.username == "emilys"

        # Convert back to model
        new_model = User()
        converted = service.schema_to_model(schema, new_model)

        assert converted.id == 1
        assert converted.first_name == "Emily"
        assert converted.last_name == "Johnson"
        assert converted.username == "emilys"

    def test_fetch_from_api(self):
        user = User(id=1, username="test")
        service = UserRestService(user)

        # Fetch user 1 from API
        schema = service.client.fetch_one(1)

        assert isinstance(schema, UserSchema)
        assert schema.id == 1
        assert schema.firstName == "Emily"
        assert schema.lastName == "Johnson"
        assert schema.username == "emilys"

    def test_fetch_many_from_api(self):
        client = DummyJsonUserClient()

        # Fetch first 5 users
        users = client.fetch_many(limit=5)

        assert isinstance(users, list)
        assert len(users) == 5
        assert all(isinstance(u, UserSchema) for u in users)
        assert users[0].firstName == "Emily"

    def test_field_mapping_model_to_schema(self):
        """Test model_to_schema using field_mapping instead of custom method."""
        # Create Django User instance
        user = User(
            id=1,
            first_name="Emily",
            last_name="Johnson",
            email="emily.johnson@example.com",
            username="emilys"
        )

        service = UserRestServiceWithMapping(user)

        # Convert to schema using default implementation with field_mapping
        schema = service.model_to_schema(user)

        assert isinstance(schema, UserSchema)
        assert schema.id == 1
        assert schema.firstName == "Emily"  # first_name -> firstName via mapping
        assert schema.lastName == "Johnson"  # last_name -> lastName via mapping
        assert schema.email == "emily.johnson@example.com"
        assert schema.username == "emilys"

    def test_field_mapping_schema_to_model(self):
        """Test schema_to_model using field_mapping instead of custom method."""
        # Fetch real user data from API
        client = DummyJsonUserClient()
        schema = client.fetch_one(1)

        temp_user = User(id=999, username="temp")
        service = UserRestServiceWithMapping(temp_user)

        # Convert to new model instance using default implementation
        new_user = service.schema_to_model(schema)

        assert isinstance(new_user, User)
        assert new_user.id == schema.id
        assert new_user.first_name == schema.firstName  # firstName -> first_name via mapping
        assert new_user.last_name == schema.lastName  # lastName -> last_name via mapping
        assert new_user.email == schema.email
        assert new_user.username == schema.username

    def test_field_mapping_schema_to_model_update_existing(self):
        """Test updating existing model using field_mapping."""
        # Create existing user with old data
        user = User(id=999, first_name="Old", last_name="Name", email="old@example.com", username="olduser")

        # Fetch real data from API
        client = DummyJsonUserClient()
        schema = client.fetch_one(1)

        service = UserRestServiceWithMapping(user)

        # Update existing model using default implementation
        updated_user = service.schema_to_model(schema, user)

        assert updated_user is user  # Same instance
        assert user.id == 1
        assert user.first_name == "Emily"  # Updated via field_mapping
        assert user.last_name == "Johnson"  # Updated via field_mapping
        assert user.username == "emilys"

    def test_field_mapping_round_trip(self):
        """Test conversion round trip using field_mapping."""
        # Create Django User
        original = User(
            id=1,
            first_name="Emily",
            last_name="Johnson",
            email="emily.johnson@example.com",
            username="emilys"
        )
        service = UserRestServiceWithMapping(original)

        # Convert to schema
        schema = service.model_to_schema(original)
        assert schema.id == 1
        assert schema.firstName == "Emily"
        assert schema.lastName == "Johnson"
        assert schema.username == "emilys"

        # Convert back to model
        new_model = User()
        converted = service.schema_to_model(schema, new_model)

        assert converted.id == 1
        assert converted.first_name == "Emily"
        assert converted.last_name == "Johnson"
        assert converted.username == "emilys"
