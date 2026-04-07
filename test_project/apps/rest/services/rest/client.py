from django_spire.contrib.rest.client.schema import RestSchemaClient
from test_project.apps.rest.services.rest.schema import UserSchema, UsersListResponseSchema


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
        if 'limit' not in params:
            params['limit'] = 10
        response = self.get(params=params)
        data = UsersListResponseSchema(**response.json())
        return data.users
