from django_spire.contrib.rest import BaseRestHttpConnector


class DummyJsonAPIRestConnector(BaseRestHttpConnector):
    base_url = 'https://dummyjson.com'