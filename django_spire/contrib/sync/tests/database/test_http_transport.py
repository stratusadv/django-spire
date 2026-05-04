from __future__ import annotations

import gzip
import json
import logging

from typing import Any
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest

from django_spire.contrib.sync.core.exceptions import (
    InvalidParameterError,
    InvalidResponseError,
    SyncAbortedError,
)
from django_spire.contrib.sync.database.transport.http import (
    HttpTransport,
    _validate_url,
)
from django_spire.contrib.sync.tests.factories import make_manifest


def _make_urlopen_response(
    data: dict[str, Any],
    content_encoding: str | None = None,
) -> MagicMock:
    body = json.dumps(data).encode('utf-8')

    if content_encoding == 'gzip':
        body = gzip.compress(body)

    response = MagicMock()
    response.read.return_value = body
    response.headers = MagicMock()
    response.headers.get.return_value = content_encoding or ''

    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=response)
    ctx.__exit__ = MagicMock(return_value=False)

    return ctx


def _valid_manifest_dict() -> dict[str, Any]:
    return make_manifest(
        node_id='server',
        checkpoint=500,
        node_time=500,
    ).to_dict()


def test_validate_url_empty_raises() -> None:
    with pytest.raises(InvalidParameterError, match='non-empty'):
        _validate_url('')


def test_validate_url_ftp_scheme_raises() -> None:
    with pytest.raises(InvalidParameterError, match='Unsupported URL scheme'):
        _validate_url('ftp://example.com/sync/')


def test_validate_url_no_scheme_raises() -> None:
    with pytest.raises(InvalidParameterError, match='Unsupported URL scheme'):
        _validate_url('example.com/sync/')


def test_validate_url_missing_host_raises() -> None:
    with pytest.raises(InvalidParameterError, match='missing a host'):
        _validate_url('http://')


def test_validate_url_http_accepted() -> None:
    _validate_url('http://example.com/sync/')


def test_validate_url_https_accepted() -> None:
    _validate_url('https://example.com/sync/')


def test_init_retries_below_one_raises() -> None:
    with pytest.raises(InvalidParameterError, match='retries'):
        HttpTransport(url='https://example.com', retries=0)


def test_init_negative_retry_delay_raises() -> None:
    with pytest.raises(InvalidParameterError, match='retry_delay'):
        HttpTransport(url='https://example.com', retry_delay=-1.0)


def test_init_zero_timeout_raises() -> None:
    with pytest.raises(InvalidParameterError, match='timeout'):
        HttpTransport(url='https://example.com', timeout=0.0)


def test_init_negative_timeout_raises() -> None:
    with pytest.raises(InvalidParameterError, match='timeout'):
        HttpTransport(url='https://example.com', timeout=-5.0)


def test_init_response_bytes_max_zero_raises() -> None:
    with pytest.raises(InvalidParameterError, match='response_bytes_max'):
        HttpTransport(url='https://example.com', response_bytes_max=0)


def test_init_warns_without_headers() -> None:
    with patch.object(logging.getLogger('django_spire.contrib.sync.database.transport.http'), 'warning') as mock_warn:
        HttpTransport(url='https://example.com')

    assert mock_warn.called


def test_init_no_warning_with_headers() -> None:
    with patch.object(logging.getLogger('django_spire.contrib.sync.database.transport.http'), 'warning') as mock_warn:
        HttpTransport(
            url='https://example.com',
            headers={'Authorization': 'Bearer token'},
        )

    assert not mock_warn.called


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_valid_response(mock_urlopen: Any) -> None:
    data = _valid_manifest_dict()
    mock_urlopen.return_value = _make_urlopen_response(data)

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
    )

    manifest = make_manifest(node_id='tablet', checkpoint=100)
    response = transport.exchange(manifest)

    assert response.node_id == 'server'
    assert response.checkpoint == 500


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_gzip_response(mock_urlopen: Any) -> None:
    data = _valid_manifest_dict()
    mock_urlopen.return_value = _make_urlopen_response(
        data, content_encoding='gzip',
    )

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
    )

    manifest = make_manifest(node_id='tablet')
    response = transport.exchange(manifest)

    assert response.node_id == 'server'


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_response_exceeds_size_limit(mock_urlopen: Any) -> None:
    oversized_body = b'x' * 200

    response_mock = MagicMock()
    response_mock.read.return_value = oversized_body
    response_mock.headers = MagicMock()
    response_mock.headers.get.return_value = ''

    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=response_mock)
    ctx.__exit__ = MagicMock(return_value=False)

    mock_urlopen.return_value = ctx

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
        response_bytes_max=100,
    )

    manifest = make_manifest(node_id='tablet')

    with pytest.raises(InvalidResponseError, match='exceeds limit'):
        transport.exchange(manifest)


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_invalid_json_raises(mock_urlopen: Any) -> None:
    response_mock = MagicMock()
    response_mock.read.return_value = b'not-json-at-all'
    response_mock.headers = MagicMock()
    response_mock.headers.get.return_value = ''

    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=response_mock)
    ctx.__exit__ = MagicMock(return_value=False)

    mock_urlopen.return_value = ctx

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
    )

    manifest = make_manifest(node_id='tablet')

    with pytest.raises(InvalidResponseError, match='not valid JSON'):
        transport.exchange(manifest)


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_non_dict_response_raises(mock_urlopen: Any) -> None:
    body = json.dumps([1, 2, 3]).encode('utf-8')

    response_mock = MagicMock()
    response_mock.read.return_value = body
    response_mock.headers = MagicMock()
    response_mock.headers.get.return_value = ''

    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=response_mock)
    ctx.__exit__ = MagicMock(return_value=False)

    mock_urlopen.return_value = ctx

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
    )

    manifest = make_manifest(node_id='tablet')

    with pytest.raises(InvalidResponseError, match='invalid response format'):
        transport.exchange(manifest)


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_missing_node_id_raises(mock_urlopen: Any) -> None:
    body = json.dumps({'checkpoint': 500}).encode('utf-8')

    response_mock = MagicMock()
    response_mock.read.return_value = body
    response_mock.headers = MagicMock()
    response_mock.headers.get.return_value = ''

    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=response_mock)
    ctx.__exit__ = MagicMock(return_value=False)

    mock_urlopen.return_value = ctx

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
    )

    manifest = make_manifest(node_id='tablet')

    with pytest.raises(InvalidResponseError, match='invalid sync response'):
        transport.exchange(manifest)


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_missing_checkpoint_raises(mock_urlopen: Any) -> None:
    body = json.dumps({'node_id': 'server'}).encode('utf-8')

    response_mock = MagicMock()
    response_mock.read.return_value = body
    response_mock.headers = MagicMock()
    response_mock.headers.get.return_value = ''

    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=response_mock)
    ctx.__exit__ = MagicMock(return_value=False)

    mock_urlopen.return_value = ctx

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
    )

    manifest = make_manifest(node_id='tablet')

    with pytest.raises(InvalidResponseError, match='invalid sync response'):
        transport.exchange(manifest)


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_http_4xx_raises_sync_aborted(mock_urlopen: Any) -> None:
    mock_urlopen.side_effect = HTTPError(
        url='https://example.com/sync/',
        code=403,
        msg='Forbidden',
        hdrs=MagicMock(),
        fp=None,
    )

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
        retries=1,
        retry_delay=0,
    )

    manifest = make_manifest(node_id='tablet')

    with pytest.raises(SyncAbortedError, match='Client error 403'):
        transport.exchange(manifest)


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_connection_error_retries(mock_urlopen: Any) -> None:
    data = _valid_manifest_dict()
    success_response = _make_urlopen_response(data)

    mock_urlopen.side_effect = [
        ConnectionError('refused'),
        success_response,
    ]

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
        retries=2,
        retry_delay=0,
    )

    manifest = make_manifest(node_id='tablet')
    response = transport.exchange(manifest)

    assert response.node_id == 'server'
    assert mock_urlopen.call_count == 2


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_timeout_retries(mock_urlopen: Any) -> None:
    data = _valid_manifest_dict()
    success_response = _make_urlopen_response(data)

    mock_urlopen.side_effect = [
        TimeoutError('timed out'),
        success_response,
    ]

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
        retries=2,
        retry_delay=0,
    )

    manifest = make_manifest(node_id='tablet')
    response = transport.exchange(manifest)

    assert response.node_id == 'server'


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_url_error_retries(mock_urlopen: Any) -> None:
    data = _valid_manifest_dict()
    success_response = _make_urlopen_response(data)

    mock_urlopen.side_effect = [
        URLError('unreachable'),
        success_response,
    ]

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
        retries=2,
        retry_delay=0,
    )

    manifest = make_manifest(node_id='tablet')
    response = transport.exchange(manifest)

    assert response.node_id == 'server'


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_malformed_gzip_response_raises(mock_urlopen: Any) -> None:
    response_mock = MagicMock()
    response_mock.read.return_value = b'not-gzip-data'
    response_mock.headers = MagicMock()
    response_mock.headers.get.return_value = 'gzip'

    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=response_mock)
    ctx.__exit__ = MagicMock(return_value=False)

    mock_urlopen.return_value = ctx

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
    )

    manifest = make_manifest(node_id='tablet')

    with pytest.raises(InvalidResponseError, match='Malformed gzip'):
        transport.exchange(manifest)


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_gzip_decompression_limit_raises(mock_urlopen: Any) -> None:
    huge = b'\x00' * 1_000_000
    compressed = gzip.compress(huge)

    response_mock = MagicMock()
    response_mock.read.return_value = compressed
    response_mock.headers = MagicMock()
    response_mock.headers.get.return_value = 'gzip'

    ctx = MagicMock()
    ctx.__enter__ = MagicMock(return_value=response_mock)
    ctx.__exit__ = MagicMock(return_value=False)

    mock_urlopen.return_value = ctx

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
        response_bytes_max=1000,
    )

    manifest = make_manifest(node_id='tablet')

    with pytest.raises(InvalidResponseError):
        transport.exchange(manifest)


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_sends_gzip_compressed_body(mock_urlopen: Any) -> None:
    data = _valid_manifest_dict()
    mock_urlopen.return_value = _make_urlopen_response(data)

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer token'},
    )

    manifest = make_manifest(node_id='tablet')
    transport.exchange(manifest)

    call_args = mock_urlopen.call_args
    request_obj = call_args[0][0]

    assert request_obj.get_header('Content-encoding') == 'gzip'
    assert request_obj.get_header('Content-type') == 'application/json'

    decompressed = gzip.decompress(request_obj.data)
    parsed = json.loads(decompressed)

    assert parsed['node_id'] == 'tablet'


@patch('django_spire.contrib.sync.database.transport.http.urlopen')
def test_exchange_includes_custom_headers(mock_urlopen: Any) -> None:
    data = _valid_manifest_dict()
    mock_urlopen.return_value = _make_urlopen_response(data)

    transport = HttpTransport(
        url='https://example.com/sync/',
        headers={'Authorization': 'Bearer my-token', 'X-Custom': 'value'},
    )

    manifest = make_manifest(node_id='tablet')
    transport.exchange(manifest)

    call_args = mock_urlopen.call_args
    request_obj = call_args[0][0]

    assert request_obj.get_header('Authorization') == 'Bearer my-token'
    assert request_obj.get_header('X-custom') == 'value'
