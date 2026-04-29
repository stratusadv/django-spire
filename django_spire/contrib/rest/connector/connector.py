
from __future__ import annotations

import inspect
import time
import urllib.parse
from abc import ABC

import requests
from django.core.exceptions import ImproperlyConfigured
from requests import HTTPError
from requests.auth import AuthBase

from django_spire.contrib.rest.connector.exceptions import \
    RestConnectorTimeoutException, RestConnectorError


class BaseRestHttpConnector(ABC):
    base_url: str
    base_path: str = ''
    base_headers: dict[str, str] = {}
    timeout: int = 30
    max_retries: int = 3

    def __init_subclass__(cls, **kwargs):
        if not inspect.isabstract(cls):
            required_attributes = ['base_url']
            for attribute in required_attributes:
                if getattr(cls, attribute, None) is None:
                    message = f'{attribute} is required'
                    raise ImproperlyConfigured(message)

            cls._validate_url(cls.base_url)

    def __init__(self):
        self._validate_url(self.base_url)

    @staticmethod
    def _validate_url(url: str) -> None:
        result = urllib.parse.urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError(f'Invalid URL: {url}')

    def _build_url(self, path: str | None = None) -> str:
        parts = [self.base_url]

        if self.base_path:
            parts.append(self.base_path)

        if path:
            parts.append(path.strip('/'))

        return '/'.join(parts)

    def request(
        self,
        method: str,
        path: str | None = None,
        headers: dict[str, str] | None = None,
        auth: bool | AuthBase | None = True,
        **kwargs,
    ) -> requests.Response:
        merged_headers = {**self.base_headers, **(headers or {})}

        if isinstance(auth, bool):
            if auth:
                auth = self.auth
            else:
                auth = None

        retries = 0

        response = requests.request(
            method=method,
            url=self._build_url(path),
            headers=merged_headers,
            auth=auth,
            timeout=self.timeout,
            **kwargs,
        )

        for i in range(self.max_retries):
            try:
                response.raise_for_status()

                break
            except requests.exceptions.Timeout as e:
                retries += 1

                if retries > 1:
                    time.sleep(retries * 2)

                if retries >= self.max_retries:
                    raise RestConnectorTimeoutException from e

                response = requests.request(
                    method=method,
                    url=self._build_url(path),
                    headers=merged_headers,
                    auth=auth,
                    timeout=self.timeout,
                    **kwargs,
                )

            except HTTPError as e:
                raise RestConnectorError from e

        return response

    def get(self, path: str | None = None, **kwargs) -> requests.Response:
        return self.request('GET', path, **kwargs)

    def post(self, path: str | None = None, **kwargs) -> requests.Response:
        return self.request('POST', path, **kwargs)

    def put(self, path: str | None = None, **kwargs) -> requests.Response:
        return self.request('PUT', path, **kwargs)

    def patch(self, path: str | None = None, **kwargs) -> requests.Response:
        return self.request('PATCH', path, **kwargs)

    def delete(self, path: str | None = None, **kwargs) -> requests.Response:
        return self.request('DELETE', path, **kwargs)

    @property
    def auth(self) -> AuthBase | None:
        return None