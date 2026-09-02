from django.http import HttpRequest
from ninja.security.apikey import APIKeyBase

from django_spire.api.choices import ApiPermissionChoices
from django_spire.api.models import ApiAccess


_API_KEY_PARAM_NAMES = ['api_key', 'User-Key', 'X-API-Key', 'Authorization', 'Bearer']


class ApiKeySecurity(APIKeyBase):
    param_name = 'api_key'
    openapi_in = 'query'

    def __init__(self, permission_required: ApiPermissionChoices | None = None) -> None:
        self.permission_required = permission_required
        super().__init__()

    def authenticate(self, request: HttpRequest, key: str | None) -> bool | ApiAccess:
        del request
        if key is None:
            return False

        api_access = ApiAccess.objects.get_by_key_or_none(key)

        if api_access is None:
            return False

        if self.permission_required is None or api_access.permission >= self.permission_required:
            return api_access

        return False

    def _get_key(self, request: HttpRequest) -> str | None:
        headers = request.headers

        for param_name in _API_KEY_PARAM_NAMES:
            key = headers.get(param_name)

            if key:
                return key

            key = request.GET.get(param_name)

            if key:
                return key

        return None
