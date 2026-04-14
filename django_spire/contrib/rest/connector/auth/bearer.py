from requests.auth import AuthBase
from requests.models import Request


class BearerAuth(AuthBase):
    def __init__(self, bearer_token) -> None:
        self._auth_header = f'Bearer {bearer_token}'

    def __call__(self, request: Request) -> Request:
        request.headers['Authorization'] = self._auth_header
        return request