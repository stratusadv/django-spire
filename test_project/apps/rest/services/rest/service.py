from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.rest.service import BaseRestService
from test_project.apps.rest.services.rest.client import DummyJsonUserClient
from test_project.apps.rest.services.rest.schema import UserSchema

if TYPE_CHECKING:
    from test_project.apps.rest.models import TestRestUser


class TestRestUserRestService(BaseRestService['TestRestUser', UserSchema, DummyJsonUserClient]):
    """REST service with custom conversion methods."""
    obj: TestRestUser
    client = DummyJsonUserClient()

    def model_to_schema(self, model: TestRestUser) -> UserSchema:
        return UserSchema(
            id=model.id or 1,
            firstName=model.first_name,
            lastName=model.last_name,
            email=model.email,
            username=model.username,
        )

    def schema_to_model(self, schema: UserSchema, model: TestRestUser | None = None) -> TestRestUser:
        if model is None:
            model = TestRestUser()
        model.id = schema.id
        model.first_name = schema.firstName
        model.last_name = schema.lastName
        model.email = schema.email
        model.username = schema.username
        return model


class TestRestUserRestServiceWithMapping(BaseRestService['TestRestUser', UserSchema, DummyJsonUserClient]):
    """REST service using field_mapping."""
    obj: TestRestUser
    client = DummyJsonUserClient()

    field_mapping = {
        'first_name': 'firstName',
        'last_name': 'lastName',
    }
