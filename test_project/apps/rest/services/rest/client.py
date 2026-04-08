from django_spire.contrib.rest.client.schema import RestSchemaClient


class PirateRestClient(RestSchemaClient):
    base_url = 'http://pirates.arrrrrr.us'

    def get(self):