from django_spire.contrib.rest_client.client import BaseRestClient
from django_spire.contrib.rest_client.schema import BaseRestSchema


class UserRestSchema(BaseRestSchema):
    first_name: str
    last_name: str


class UserRestClient(BaseRestClient):
    rest_schema_class = UserRestSchema
    base_url = 'https://rest.spire.com'


# user_rest_client = UserRestClient()

user = UserRestClient.get('stuff').to_dict()
