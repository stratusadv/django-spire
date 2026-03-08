from ninja.security import APIKeyQuery, APIKeyHeader

from django_spire.api.models import ApiAccess


class ApiKeyQuerySecurity(APIKeyQuery):
    param_name = "api_key"

    def authenticate(self, request, key):
        return key and ApiAccess.objects.is_valid_key(key)


class ApiKeyHeaderSecurity(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key):
        return key and ApiAccess.objects.is_valid_key(key)
