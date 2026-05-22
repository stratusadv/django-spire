from requests.auth import AuthBase
from requests.models import Request


class BearerAuth(AuthBase):
    auth_header_name = 'Authorization'

    def __init__(self, bearer_token) -> None:
        self._auth_header = f'Bearer {bearer_token}'

    def __call__(self, request: Request) -> Request:
        request.headers[self.auth_header_name] = self._auth_header
        return request