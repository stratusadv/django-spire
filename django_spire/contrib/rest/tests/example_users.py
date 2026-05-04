from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.rest import BaseRestHttpConnector, RestSchema, RestSchemaSet

if TYPE_CHECKING:
    pass


class DummyJsonConnector(BaseRestHttpConnector):
    """Connector for DummyJSON API."""
    base_url = 'https://dummyjson.com'


class UserSchemaSet(RestSchemaSet['UserSchema']):
    """SchemaSet for DummyJSON Users API."""
    connector = DummyJsonConnector()

    def _read_many(self, **request_params) -> list['UserSchema']:
        from django_spire.contrib.rest.tests.example_users import UserSchema

        response = self.connector.get('users', params=request_params)
        data = response.json()

        return [UserSchema(**user) for user in data.get('users', [])]


class UserSchema(RestSchema):
    """Schema for DummyJSON User API."""
    id: int
    firstName: str
    lastName: str
    email: str
    username: str

    objects = UserSchemaSet.as_manager()
