from django.http import HttpRequest
from ninja.security.apikey import APIKeyBase

from django_spire.api.choices import ApiPermissionChoices
from django_spire.api.models import ApiAccess

_API_KEY_PARAM_NAMES = ['api_key', 'User-Key', 'X-API-Key', 'Authorization', 'Bearer']


class ApiKeySecurity(APIKeyBase):
    param_name = 'api_key'
    openapi_in = 'query'

    def __init__(
            self,
            api_permission_required: ApiPermissionChoices | None = None,
            user_permission_required: str | None = None,
    ) -> None:
        self.api_permission_required = api_permission_required
        self.user_permission_required = user_permission_required
        super().__init__()

    def authenticate(self, request: HttpRequest, key: str | None) -> bool | ApiAccess:
        if key is None:
            return False

        api_access = ApiAccess.objects.get_by_key_or_none(key)

        if api_access is None:
            return False

        if (
                self.api_permission_required is not None
                and api_access.permission < self.api_permission_required
        ):
            return False

        if (
                self.user_permission_required is not None
                and (api_access.user is None
                     or not api_access.user.has_perm(self.user_permission_required))
        ):
            return False

        return self._authorize_request(request, api_access)

    def _authorize_request(self, request: HttpRequest, api_access: ApiAccess) -> ApiAccess:
        if request is not None and api_access.user is not None:
            request.user = api_access.user

        return api_access

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
