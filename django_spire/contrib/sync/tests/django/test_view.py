from __future__ import annotations

import gzip
import json

from typing import Any
from unittest.mock import MagicMock

import pytest

from django.test import RequestFactory

from django_spire.contrib.sync.core.exceptions import (
    InvalidParameterError,
    ManifestChecksumError,
    SyncAbortedError,
)
from django_spire.contrib.sync.database.manifest import (
    DatabaseResult,
    ModelPayload,
    SyncManifest,
)
from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.django.views import process_sync_request
from django_spire.contrib.sync.tests.factories import make_manifest


@pytest.fixture
def factory() -> RequestFactory:
    return RequestFactory()


@pytest.fixture
def mock_engine() -> MagicMock:
    engine = MagicMock()

    response = SyncManifest(
        node_id='server',
        checkpoint=500,
        node_time=500,
        payloads=[],
    )
    response.checksum = response.compute_checksum()

    result = DatabaseResult()

    engine.process.return_value = (response, result)

    return engine


def _make_post(
    factory: RequestFactory,
    data: dict[str, Any],
    content_type: str = 'application/json',
    content_encoding: str | None = None,
) -> Any:
    body = json.dumps(data).encode('utf-8')

    if content_encoding == 'gzip':
        body = gzip.compress(body)

    request = factory.post(
        '/sync/',
        data=body,
        content_type=content_type,
    )

    if content_encoding:
        request.META['HTTP_CONTENT_ENCODING'] = content_encoding

    return request


def test_post_returns_json(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    manifest = make_manifest(node_id='tablet', checkpoint=0, node_time=100)
    request = _make_post(factory, manifest.to_dict())

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 200

    data = json.loads(response.content)

    assert data['node_id'] == 'server'


def test_post_passes_manifest_to_engine(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    manifest = make_manifest(
        node_id='tablet-5',
        checkpoint=100,
        node_time=101,
        payloads=[
            ModelPayload(
                model_label='app.Model',
                records={
                    '1': SyncRecord(
                        key='1',
                        data={'name': 'Alice'},
                        timestamps={'name': 100},
                    ),
                },
            ),
        ],
    )

    request = _make_post(factory, manifest.to_dict())

    process_sync_request(request, mock_engine)

    mock_engine.process.assert_called_once()

    incoming = mock_engine.process.call_args[0][0]

    assert incoming.node_id == 'tablet-5'
    assert len(incoming.payloads) == 1


def test_method_not_allowed(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.get('/sync/')

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 405


def test_wrong_content_type(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.post(
        '/sync/',
        data=b'{}',
        content_type='text/plain',
    )

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 415


def test_oversized_content_length_header(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.post(
        '/sync/',
        data=b'{}',
        content_type='application/json',
    )
    request.META['CONTENT_LENGTH'] = '999999999'

    response = process_sync_request(
        request, mock_engine, request_bytes_max=1000,
    )

    assert response.status_code == 413


def test_invalid_content_length_header(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.post(
        '/sync/',
        data=b'{}',
        content_type='application/json',
    )
    request.META['CONTENT_LENGTH'] = 'not-a-number'

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 400


def test_negative_content_length_header(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.post(
        '/sync/',
        data=b'{}',
        content_type='application/json',
    )
    request.META['CONTENT_LENGTH'] = '-1'

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 400


def test_body_too_large(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.post(
        '/sync/',
        data=b'x' * 200,
        content_type='application/json',
    )

    response = process_sync_request(
        request, mock_engine, request_bytes_max=100,
    )

    assert response.status_code == 413


def test_gzip_body_decompressed(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    manifest = make_manifest(node_id='tablet', checkpoint=0, node_time=100)
    request = _make_post(
        factory, manifest.to_dict(), content_encoding='gzip',
    )

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 200


def test_gzip_decompression_bomb_rejected(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    huge = b'\x00' * 1_000_000
    compressed = gzip.compress(huge)

    request = factory.post(
        '/sync/',
        data=compressed,
        content_type='application/json',
    )
    request.META['HTTP_CONTENT_ENCODING'] = 'gzip'

    response = process_sync_request(
        request, mock_engine, request_bytes_max=10_000,
    )

    assert response.status_code == 413


def test_malformed_gzip_rejected(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.post(
        '/sync/',
        data=b'not-gzip-data',
        content_type='application/json',
    )
    request.META['HTTP_CONTENT_ENCODING'] = 'gzip'

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 400


def test_invalid_json_rejected(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.post(
        '/sync/',
        data=b'{not valid json',
        content_type='application/json',
    )

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 400


def test_non_dict_json_rejected(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.post(
        '/sync/',
        data=json.dumps([1, 2, 3]).encode('utf-8'),
        content_type='application/json',
    )

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 400


def test_malformed_manifest_rejected(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    request = factory.post(
        '/sync/',
        data=json.dumps({'garbage': True}).encode('utf-8'),
        content_type='application/json',
    )

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 400


def test_engine_sync_aborted_returns_409(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    mock_engine.process.side_effect = SyncAbortedError('drift')

    manifest = make_manifest(node_id='tablet')
    request = _make_post(factory, manifest.to_dict())

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 409

    data = json.loads(response.content)

    assert data['ok'] is False


def test_engine_manifest_checksum_error_returns_409(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    mock_engine.process.side_effect = ManifestChecksumError('bad checksum')

    manifest = make_manifest(node_id='tablet')
    request = _make_post(factory, manifest.to_dict())

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 409


def test_validate_node_id_rejection(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    manifest = make_manifest(node_id='tablet')
    request = _make_post(factory, manifest.to_dict())

    def reject_all(req: Any, node_id: str) -> bool:
        _ = req
        _ = node_id

        return False

    response = process_sync_request(
        request, mock_engine, validate_node_id=reject_all,
    )

    assert response.status_code == 403

    mock_engine.process.assert_not_called()


def test_validate_node_id_acceptance(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    manifest = make_manifest(node_id='tablet')
    request = _make_post(factory, manifest.to_dict())

    def accept_all(req: Any, node_id: str) -> bool:
        _ = req
        _ = node_id

        return True

    response = process_sync_request(
        request, mock_engine, validate_node_id=accept_all,
    )

    assert response.status_code == 200


def test_request_bytes_max_below_one_raises(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    manifest = make_manifest(node_id='tablet')
    request = _make_post(factory, manifest.to_dict())

    with pytest.raises(InvalidParameterError, match='request_bytes_max'):
        process_sync_request(request, mock_engine, request_bytes_max=0)


def test_no_content_length_header_passes(
    factory: RequestFactory,
    mock_engine: MagicMock,
) -> None:
    manifest = make_manifest(node_id='tablet')
    request = _make_post(factory, manifest.to_dict())

    if 'CONTENT_LENGTH' in request.META:
        del request.META['CONTENT_LENGTH']

    response = process_sync_request(request, mock_engine)

    assert response.status_code == 200
