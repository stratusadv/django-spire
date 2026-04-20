from typing import TYPE_CHECKING

from django_spire.contrib.rest import RestSchemaSet
from test_project.apps.rest.rest.connector import DummyJsonAPIRestConnector

if TYPE_CHECKING:
    from test_project.apps.rest.rest.schema import PirateRestSchema


class PirateRestSchemaSet(RestSchemaSet['PirateRestSchema']):
    connector = DummyJsonAPIRestConnector()

    def _read_many(self, **request_params) -> list['PirateRestSchema']:
        from test_project.apps.rest.rest.schema import PirateRestSchema

        response = self.connector.get('users', params=request_params)
        data = response.json()

        return [PirateRestSchema(**user) for user in data.get('users', [])]