# from __future__ import annotations

# import json
# import logging

# from django.http import JsonResponse
# from django.utils.decorators import method_decorator
# from django.views import View
# from django.views.decorators.csrf import csrf_exempt

# from django_spire.contrib.sync.core.compression import safe_gzip_decompress
# from django_spire.contrib.sync.core.exceptions import (
#     DecompressionLimitError,
#     ManifestFieldError,
#     SyncAbortedError,
# )
# from django_spire.contrib.sync.database.manifest import SyncManifest

# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from django.http import HttpRequest, HttpResponse

#     from django_spire.contrib.sync.database.engine import DatabaseEngine


# logger = logging.getLogger(__name__)

# _REQUEST_BYTES_MAX = 50 * 1024 * 1024


# @method_decorator(csrf_exempt, name='dispatch')
# class SyncView(View):
#     engine: DatabaseEngine | None = None
#     request_bytes_max: int = _REQUEST_BYTES_MAX

#     def dispatch(
#         self,
#         request: HttpRequest,
#         *args: object,
#         **kwargs: object,
#     ) -> HttpResponse:
#         if not request.user.is_authenticated:
#             return JsonResponse(
#                 {'ok': False, 'error': 'Authentication required'},
#                 status=401,
#             )

#         if not self.has_sync_permission(request):
#             return JsonResponse(
#                 {'ok': False, 'error': 'Insufficient permissions'},
#                 status=403,
#             )

#         return super().dispatch(request, *args, **kwargs)

#     def get_engine(self) -> DatabaseEngine:
#         if self.engine is None:
#             message = (
#                 'SyncView.engine must be set. '
#                 'Override get_engine() or set engine on the class.'
#             )
#             raise NotImplementedError(message)

#         return self.engine

#     def has_sync_permission(self, request: HttpRequest) -> bool:
#         return request.user.is_staff

#     def validate_node_id(self, request: HttpRequest, node_id: str) -> bool:
#         _ = request
#         _ = node_id
#         return True

#     def _reject_if_oversized_header(
#         self,
#         request: HttpRequest,
#     ) -> JsonResponse | None:
#         raw_length = request.META.get('CONTENT_LENGTH')

#         if not raw_length:
#             return None

#         try:
#             declared = int(raw_length)
#         except (TypeError, ValueError):
#             return JsonResponse(
#                 {'ok': False, 'error': 'Invalid Content-Length header'},
#                 status=400,
#             )

#         if declared < 0:
#             return JsonResponse(
#                 {'ok': False, 'error': 'Invalid Content-Length header'},
#                 status=400,
#             )

#         if declared > self.request_bytes_max:
#             return JsonResponse(
#                 {'ok': False, 'error': 'Request body too large'},
#                 status=413,
#             )

#         return None

#     def post(self, request: HttpRequest) -> JsonResponse:
#         engine = self.get_engine()

#         content_type = request.content_type or ''

#         if content_type != 'application/json':
#             return JsonResponse(
#                 {'ok': False, 'error': 'Content-Type must be application/json'},
#                 status=415,
#             )

#         header_response = self._reject_if_oversized_header(request)

#         if header_response is not None:
#             return header_response

#         body = request.body

#         if len(body) > self.request_bytes_max:
#             return JsonResponse(
#                 {'ok': False, 'error': 'Request body too large'},
#                 status=413,
#             )

#         if request.headers.get('Content-Encoding') == 'gzip':
#             try:
#                 body = safe_gzip_decompress(body, self.request_bytes_max)
#             except DecompressionLimitError:
#                 return JsonResponse(
#                     {'ok': False, 'error': 'Decompressed request body too large'},
#                     status=413,
#                 )
#             except Exception as exception:
#                 logger.warning('Failed to decompress gzip body: %s', exception)

#                 return JsonResponse(
#                     {'ok': False, 'error': 'Failed to decompress request body'},
#                     status=400,
#                 )

#         try:
#             data = json.loads(body)
#         except (json.JSONDecodeError, UnicodeDecodeError) as exception:
#             logger.warning('Invalid JSON in sync request: %s', exception)

#             return JsonResponse(
#                 {'ok': False, 'error': 'Invalid JSON in request body'},
#                 status=400,
#             )

#         if not isinstance(data, dict):
#             return JsonResponse(
#                 {'ok': False, 'error': 'Request body must be a JSON object'},
#                 status=400,
#             )

#         try:
#             incoming = SyncManifest.from_dict(data)
#         except (KeyError, TypeError, ManifestFieldError) as exception:
#             logger.warning('Malformed sync manifest: %s', exception)

#             return JsonResponse(
#                 {'ok': False, 'error': 'Malformed sync manifest'},
#                 status=400,
#             )

#         if not self.validate_node_id(request, incoming.node_id):
#             return JsonResponse(
#                 {'ok': False, 'error': 'Node ID not authorized for this user'},
#                 status=403,
#             )

#         logger.info(
#             'Received sync from node %s with %d payloads',
#             incoming.node_id,
#             len(incoming.payloads),
#         )

#         try:
#             response, result = engine.process(incoming)
#         except SyncAbortedError as exception:
#             logger.exception(
#                 'Sync aborted for node %s',
#                 incoming.node_id,
#             )

#             return JsonResponse(
#                 {'ok': False, 'error': str(exception)},
#                 status=409,
#             )
#         else:
#             return JsonResponse({
#                 **response.to_dict(),
#                 'ok': result.ok,
#                 'errors': [
#                     {'key': error.key, 'message': error.message}
#                     for error in result.errors
#                 ],
#             })
