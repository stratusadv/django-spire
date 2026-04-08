# Django Spire REST Module
#
# Provides two patterns for REST API integration:
#
# 1. RestSchema (recommended) - Simple, Django-like pattern:
#    class UserSchema(RestSchema):
#        id: int
#        name: str
#        class Meta:
#            base_url = 'https://api.example.com'
#            base_path = 'users'
#    users = UserSchema.objects.all()
#
# 2. RestSchemaClient (legacy) - More verbose, separate schema/client:
#    class UserClient(RestSchemaClient[UserSchema]):
#        base_url = 'https://api.example.com'
#        def fetch_many(self, **params): ...
#    users = UserClient.objects.all()

from django_spire.contrib.rest.schema import RestSchema
from django_spire.contrib.rest.queryset import RestSchemaSet

__all__ = ['RestSchema', 'RestSchemaSet']
