from __future__ import annotations

import json
import logging

from typing import TYPE_CHECKING

from django.http import JsonResponse

from django_spire.contrib.sync.core.compression import safe_gzip_decompress
from django_spire.contrib.sync.core.exceptions import (
    DecompressionLimitError,
    ManifestFieldError,
    SyncAbortedError,
)
from django_spire.contrib.sync.database.manifest import SyncManifest

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest

    from django_spire.contrib.sync.database.engine import DatabaseEngine


logger = logging.getLogger(__name__)

_REQUEST_BYTES_MAX = 50 * 1024 * 1024


def process_sync_request(
    request: HttpRequest,
    engine: DatabaseEngine,
    request_bytes_max: int = _REQUEST_BYTES_MAX,
    validate_node_id: Callable[[HttpRequest, str], bool] | None = None,
) -> JsonResponse:
    if request.method != 'POST':
        return JsonResponse(
            {'ok': False, 'error': 'Method not allowed'},
            status=405,
        )

    content_type = request.content_type or ''

    if content_type != 'application/json':
        return JsonResponse(
            {'ok': False, 'error': 'Content-Type must be application/json'},
            status=415,
        )

    rejection = _reject_if_oversized_header(request, request_bytes_max)

    if rejection is not None:
        return rejection

    body = request.body

    if len(body) > request_bytes_max:
        return JsonResponse(
            {'ok': False, 'error': 'Request body too large'},
            status=413,
        )

    if request.headers.get('Content-Encoding') == 'gzip':
        try:
            body = safe_gzip_decompress(body, request_bytes_max)
        except DecompressionLimitError:
            return JsonResponse(
                {'ok': False, 'error': 'Decompressed request body too large'},
                status=413,
            )
        except Exception:
            logger.exception('Failed to decompress gzip body')

            return JsonResponse(
                {'ok': False, 'error': 'Failed to decompress request body'},
                status=400,
            )

    try:
        data = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.exception('Invalid JSON in sync request')

        return JsonResponse(
            {'ok': False, 'error': 'Invalid JSON in request body'},
            status=400,
        )

    if not isinstance(data, dict):
        return JsonResponse(
            {'ok': False, 'error': 'Request body must be a JSON object'},
            status=400,
        )

    try:
        incoming = SyncManifest.from_dict(data)
    except (KeyError, TypeError, ManifestFieldError):
        logger.exception('Malformed sync manifest')

        return JsonResponse(
            {'ok': False, 'error': 'Malformed sync manifest'},
            status=400,
        )

    if validate_node_id is not None and not validate_node_id(request, incoming.node_id):
        return JsonResponse(
            {'ok': False, 'error': 'Node ID not authorized for this user'},
            status=403,
        )

    logger.info(
        'Received sync from node %s with %d payloads',
        incoming.node_id,
        len(incoming.payloads),
    )

    try:
        response, result = engine.process(incoming)
    except SyncAbortedError:
        logger.exception(
            'Sync aborted for node %s',
            incoming.node_id,
        )

        return JsonResponse(
            {'ok': False, 'error': 'Sync aborted'},
            status=409,
        )
    else:
        return JsonResponse({
            **response.to_dict(),
            'ok': result.ok,
            'errors': [
                {'key': error.key, 'message': error.message}
                for error in result.errors
            ],
        })


def _reject_if_oversized_header(
    request: HttpRequest,
    request_bytes_max: int,
) -> JsonResponse | None:
    raw_length = request.META.get('CONTENT_LENGTH')

    if not raw_length:
        return None

    try:
        declared = int(raw_length)
    except (TypeError, ValueError):
        return JsonResponse(
            {'ok': False, 'error': 'Invalid Content-Length header'},
            status=400,
        )

    if declared < 0:
        return JsonResponse(
            {'ok': False, 'error': 'Invalid Content-Length header'},
            status=400,
        )

    if declared > request_bytes_max:
        return JsonResponse(
            {'ok': False, 'error': 'Request body too large'},
            status=413,
        )

    return None
