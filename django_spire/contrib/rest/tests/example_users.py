from __future__ import annotations

from django.contrib.auth.models import User

from django_spire.contrib.rest import RestSchema
from django_spire.contrib.rest.service import BaseRestService


class UserSchema(RestSchema):
    """Schema for DummyJSON User API."""
    id: int
    firstName: str
    lastName: str
    email: str
    username: str

    class Meta:
        base_url = 'https://dummyjson.com'
        base_path = 'users'
        results_key = 'users'


class UserRestService(BaseRestService[User, UserSchema]):
    """REST service for Django User model with DummyJSON API."""
    obj: User

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


class UserRestServiceWithMapping(BaseRestService[User, UserSchema]):
    """REST service using field_mapping instead of custom conversion methods."""
    obj: User

    # Map Django User model fields to API schema fields
    field_mapping = {
        'first_name': 'firstName',
        'last_name': 'lastName',
    }
    # id, email, and username map directly (same field names)
