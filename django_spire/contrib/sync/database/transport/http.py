from __future__ import annotations

import gzip
import json
import logging

from socket import timeout as socket_timeout
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django_spire.contrib.sync.core.compression import (
    gzip_decompress,
)
from django_spire.contrib.sync.core.exceptions import (
    DecompressionLimitError,
    InvalidParameterError,
    InvalidResponseError,
    SyncAbortedError,
)
from django_spire.contrib.sync.core.retry import retry
from django_spire.contrib.sync.database.manifest import SyncManifest
from django_spire.contrib.sync.database.transport.base import Transport


logger = logging.getLogger(__name__)

_ALLOWED_SCHEMES = frozenset({'http', 'https'})
_RESPONSE_BYTES_MAX = 50 * 1024 * 1024

_TRANSIENT_EXCEPTIONS: tuple[type[BaseException], ...] = (
    ConnectionError,
    TimeoutError,
    URLError,
    socket_timeout,
)


def _validate_url(url: str) -> None:
    if not url:
        message = 'url must be a non-empty string'
        raise InvalidParameterError(message)

    parsed = urlparse(url)

    if parsed.scheme not in _ALLOWED_SCHEMES:
        message = (
            f'Unsupported URL scheme: {parsed.scheme!r}. '
            f'Only http and https are allowed.'
        )

        raise InvalidParameterError(message)

    if not parsed.netloc:
        message = f'URL is missing a host: {url!r}'
        raise InvalidParameterError(message)


class HttpTransport(Transport):
    def __init__(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 30.0,
        response_bytes_max: int = _RESPONSE_BYTES_MAX,
    ) -> None:
        _validate_url(url)

        if retries < 1:
            message = f'retries must be >= 1, got {retries}'
            raise InvalidParameterError(message)

        if retry_delay < 0.0:
            message = (
                f'retry_delay must be non-negative, '
                f'got {retry_delay}'
            )

            raise InvalidParameterError(message)

        if timeout <= 0.0:
            message = f'timeout must be positive, got {timeout}'
            raise InvalidParameterError(message)

        if response_bytes_max < 1:
            message = (
                f'response_bytes_max must be >= 1, '
                f'got {response_bytes_max}'
            )

            raise InvalidParameterError(message)

        self._headers = headers or {}
        self._response_bytes_max = response_bytes_max
        self._retries = retries
        self._retry_delay = retry_delay
        self._timeout = timeout
        self._url = url

        if not self._headers:
            logger.warning(
                'HttpTransport created without '
                'auth headers for %s',
                self._url,
            )

    def _post(self, data: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(data).encode('utf-8')
        compressed = gzip.compress(body)

        headers = {
            'Accept-Encoding': 'gzip',
            'Content-Encoding': 'gzip',
            'Content-Type': 'application/json',
            **self._headers,
        }

        request = Request(  # noqa: S310
            self._url,
            data=compressed,
            headers=headers,
            method='POST',
        )

        try:
            with urlopen(request, timeout=self._timeout) as response:  # noqa: S310
                raw = response.read(self._response_bytes_max + 1)

                if len(raw) > self._response_bytes_max:
                    message = (
                        f'Response size exceeds limit '
                        f'of {self._response_bytes_max} '
                        f'bytes'
                    )

                    raise InvalidResponseError(message)

                encoding = response.headers.get('Content-Encoding')

                if encoding == 'gzip':
                    raw = self._decompress_response(raw)

                return self._parse_json(raw)
        except HTTPError as exception:
            if 400 <= exception.code < 500:
                message = (
                    f'Client error {exception.code}: '
                    f'{exception.reason}'
                )

                raise SyncAbortedError(message) from exception

            raise

    def _decompress_response(self, raw: bytes) -> bytes:
        try:
            return gzip_decompress(raw, self._response_bytes_max)
        except DecompressionLimitError as exception:
            raise InvalidResponseError(str(exception)) from exception
        except (gzip.BadGzipFile, EOFError, OSError) as exception:
            message = f'Malformed gzip response: {exception}'
            raise InvalidResponseError(message) from exception

    def _parse_json(self, raw: bytes) -> dict[str, Any]:
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exception:
            message = (
                f'Response body is not valid JSON: '
                f'{exception}'
            )

            raise InvalidResponseError(message) from exception

    def exchange(
        self, manifest: SyncManifest,
    ) -> SyncManifest:
        payload = manifest.to_dict()

        response_data = retry(
            lambda: self._post(payload),
            attempts=self._retries,
            delay=self._retry_delay,
            exceptions=_TRANSIENT_EXCEPTIONS,
        )

        if not isinstance(response_data, dict):
            message = 'Server returned an invalid response format'
            raise InvalidResponseError(message)

        if 'node_id' not in response_data:
            error = response_data.get(
                'error',
                'Missing required manifest fields',
            )

            message = (
                f'Server returned an invalid sync '
                f'response: {error}'
            )

            raise InvalidResponseError(message)

        if 'checkpoint' not in response_data:
            error = response_data.get(
                'error',
                'Missing required manifest fields',
            )

            message = (
                f'Server returned an invalid sync '
                f'response: {error}'
            )

            raise InvalidResponseError(message)

        logger.info(
            'Exchanged manifest with %s '
            '(%d payloads sent, %d received)',
            self._url,
            len(manifest.payloads),
            len(response_data.get('payloads', [])),
        )

        return SyncManifest.from_dict(response_data)
