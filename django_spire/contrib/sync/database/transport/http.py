from __future__ import annotations

import gzip
import json
import logging

from socket import timeout as socket_timeout
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from django_spire.contrib.sync.core.compression import safe_gzip_decompress
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
    URLError,
    TimeoutError,
    socket_timeout,
    ConnectionError,
)


def _validate_url_scheme(url: str) -> None:
    parsed = urlparse(url)

    if parsed.scheme not in _ALLOWED_SCHEMES:
        message = (
            f'Unsupported URL scheme: {parsed.scheme!r}. '
            f'Only http and https are allowed.'
        )
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
        _validate_url_scheme(url)

        self._headers = headers or {}
        self._response_bytes_max = response_bytes_max
        self._retries = retries
        self._retry_delay = retry_delay
        self._timeout = timeout
        self._url = url

        if not self._headers:
            logger.warning(
                'HttpTransport created without auth headers for %s',
                self._url,
            )

    def _post(self, data: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(data).encode('utf-8')
        compressed = gzip.compress(body)

        headers = {
            'Content-Type': 'application/json',
            'Content-Encoding': 'gzip',
            'Accept-Encoding': 'gzip',
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
                        f'Response size exceeds limit of '
                        f'{self._response_bytes_max} bytes'
                    )
                    raise InvalidResponseError(message)

                if response.headers.get('Content-Encoding') == 'gzip':
                    try:
                        raw = safe_gzip_decompress(
                            raw, self._response_bytes_max,
                        )
                    except DecompressionLimitError as exception:
                        raise InvalidResponseError(str(exception)) from exception
                    except (gzip.BadGzipFile, EOFError, OSError) as exception:
                        message = f'Malformed gzip response: {exception}'
                        raise InvalidResponseError(message) from exception

                try:
                    return json.loads(raw)
                except (json.JSONDecodeError, UnicodeDecodeError) as exception:
                    message = f'Response body is not valid JSON: {exception}'
                    raise InvalidResponseError(message) from exception
        except HTTPError as exception:
            if 400 <= exception.code < 500:
                message = f'Client error {exception.code}: {exception.reason}'
                raise SyncAbortedError(message) from exception

            raise

    def exchange(self, manifest: SyncManifest) -> SyncManifest:
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

        if 'node_id' not in response_data or 'checkpoint' not in response_data:
            error = response_data.get('error', 'Missing required manifest fields')

            message = f'Server returned an invalid sync response: {error}'
            raise InvalidResponseError(message)

        logger.info(
            'Exchanged manifest with %s (%d payloads sent, %d received)',
            self._url,
            len(manifest.payloads),
            len(response_data.get('payloads', [])),
        )

        return SyncManifest.from_dict(response_data)
