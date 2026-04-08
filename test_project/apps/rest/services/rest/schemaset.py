from django_spire.contrib.rest import RestSchemaSet
from test_project.apps.rest.services.rest.client import PirateRestClient


class PirateRestSchemaSet(RestSchemaSet):
    rest_client = PirateRestClient

    def hats(self):
        return ...

    def by_wicked_ship_name(self):
        return ...