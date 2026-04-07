from __future__ import annotations

from django.contrib.auth.models import User
from pydantic import BaseModel

from django_spire.contrib.rest.client.schema import RestSchemaClient
from django_spire.contrib.rest.service import BaseRestService


# DummyJSON User API Schemas (simplified - only fields we need for testing)
class UserSchema(BaseModel):
    """Schema for DummyJSON User API."""
    id: int
    firstName: str
    lastName: str
    email: str
    username: str


class UsersListResponseSchema(BaseModel):
    """Response schema for /users endpoint."""
    users: list[UserSchema]
    total: int
    skip: int
    limit: int


class DummyJsonUserClient(RestSchemaClient[UserSchema]):
    """Client for DummyJSON Users API."""
    base_url = 'https://dummyjson.com'
    base_path = 'users'

    def fetch_one(self, user_id: str | int) -> UserSchema:
        """Fetch a single user by ID."""
        response = self.get(path=str(user_id))
        return UserSchema(**response.json())

    def fetch_many(self, **params) -> list[UserSchema]:
        """Fetch multiple users."""
        # Default to limit=10 if not specified
        if 'limit' not in params:
            params['limit'] = 10

        response = self.get(params=params)
        data = UsersListResponseSchema(**response.json())
        return data.users


class UserRestService(BaseRestService[User, UserSchema, DummyJsonUserClient]):
    """REST service for Django User model with DummyJSON API."""
    obj: User
    client = DummyJsonUserClient()

    # Custom conversion since Django User fields don't match API fields
    def model_to_schema(self, model: User) -> UserSchema:
        """Convert Django User to UserSchema."""
        return UserSchema(
            id=model.id or 1,
            firstName=model.first_name,
            lastName=model.last_name,
            email=model.email,
            username=model.username,
        )

    def schema_to_model(self, schema: UserSchema, model: User | None = None) -> User:
        """Convert UserSchema to Django User."""
        if model is None:
            model = User()

        model.id = schema.id
        model.first_name = schema.firstName
        model.last_name = schema.lastName
        model.email = schema.email
        model.username = schema.username

        return model


class UserRestServiceWithMapping(BaseRestService[User, UserSchema, DummyJsonUserClient]):
    """REST service using field_mapping instead of custom conversion methods."""
    obj: User
    client = DummyJsonUserClient()

    # Map Django User model fields to API schema fields
    field_mapping = {
        'first_name': 'firstName',
        'last_name': 'lastName',
    }
    # id, email, and username map directly (same field names)
