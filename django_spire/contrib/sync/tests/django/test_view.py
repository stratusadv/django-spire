# from __future__ import annotations

# import gzip
# import json

# from typing import Any
# from unittest.mock import MagicMock

# import pytest

# from django.test import RequestFactory

# from django_spire.contrib.sync.core.model import Error
# from django_spire.contrib.sync.database.engine import DatabaseEngine
# from django_spire.contrib.sync.database.manifest import (
#     DatabaseResult,
#     ModelPayload,
#     SyncManifest,
# )
# from django_spire.contrib.sync.database.record import SyncRecord
# from django_spire.contrib.sync.django.views import SyncView


# @pytest.fixture
# def factory() -> RequestFactory:
#     return RequestFactory()


# @pytest.fixture
# def mock_engine() -> MagicMock:
#     engine = MagicMock(spec=DatabaseEngine)

#     response = SyncManifest(
#         node_id='server',
#         checkpoint=500,
#         node_time=500,
#         payloads=[],
#     )

#     result = DatabaseResult()

#     engine.process.return_value = (response, result)

#     return engine


# @pytest.fixture
# def view(mock_engine: MagicMock) -> SyncView:
#     v = SyncView()
#     v.engine = mock_engine
#     return v


# def _make_staff_request(
#     factory: RequestFactory,
#     data: dict[str, Any],
#     content_encoding: str | None = None,
# ) -> Any:
#     body = json.dumps(data).encode('utf-8')

#     if content_encoding == 'gzip':
#         body = gzip.compress(body)

#     request = factory.post(
#         '/sync/',
#         data=body,
#         content_type='application/json',
#     )

#     if content_encoding:
#         request.META['HTTP_CONTENT_ENCODING'] = content_encoding

#     user = MagicMock()
#     user.is_authenticated = True
#     user.is_staff = True
#     request.user = user

#     return request


# @pytest.mark.django_db
# def test_post_returns_json(
#     factory: RequestFactory,
#     view: SyncView,
# ) -> None:
#     manifest = SyncManifest(
#         node_id='tablet',
#         checkpoint=0,
#         node_time=100,
#         payloads=[],
#     )

#     request = _make_staff_request(factory, manifest.to_dict())

#     response = view.post(request)

#     assert response.status_code == 200

#     data = json.loads(response.content)

#     assert data['node_id'] == 'server'
#     assert data['ok'] is True


# @pytest.mark.django_db
# def test_post_passes_manifest_to_engine(
#     factory: RequestFactory,
#     view: SyncView,
#     mock_engine: MagicMock,
# ) -> None:
#     manifest = SyncManifest(
#         node_id='tablet-5',
#         checkpoint=100,
#         node_time=101,
#         payloads=[
#             ModelPayload(
#                 model_label='app.Model',
#                 records={
#                     '1': SyncRecord(key='1', data={'name': 'Alice'}, timestamps={}),
#                 },
#             ),
#         ],
#     )

#     request = _make_staff_request(factory, manifest.to_dict())

#     view.post(request)

#     mock_engine.process.assert_called_once()

#     incoming = mock_engine.process.call_args[0][0]

#     assert incoming.node_id == 'tablet-5'
#     assert len(incoming.payloads) == 1


# @pytest.mark.django_db
# def test_post_includes_errors_in_response(
#     factory: RequestFactory,
#     mock_engine: MagicMock,
# ) -> None:
#     _ = factory

#     result = DatabaseResult()
#     result.errors.append(Error(key='1', message='bad record'))

#     response_manifest = SyncManifest(
#         node_id='server',
#         checkpoint=500,
#         node_time=500,
#         payloads=[],
#     )

#     mock_engine.process.return_value = (response_manifest, result)

#     v = SyncView()
#     v.engine = mock_engine

#     manifest = SyncManifest(
#         node_id='tablet',
#         checkpoint=0,
#         node_time=100,
#         payloads=[],
#     )

#     request = _make_staff_request(RequestFactory(), manifest.to_dict())

#     response = v.post(request)
#     data = json.loads(response.content)

#     assert data['ok'] is False
#     assert len(data['errors']) == 1
#     assert data['errors'][0]['key'] == '1'


# @pytest.mark.django_db
# def test_get_engine_raises_when_not_set() -> None:
#     view = SyncView()

#     with pytest.raises(NotImplementedError, match='engine must be set'):
#         view.get_engine()


# @pytest.mark.django_db
# def test_dispatch_rejects_non_staff(
#     factory: RequestFactory,
#     view: SyncView,
# ) -> None:
#     manifest = SyncManifest(
#         node_id='tablet',
#         checkpoint=0,
#         node_time=100,
#         payloads=[],
#     )

#     request = factory.post(
#         '/sync/',
#         data=json.dumps(manifest.to_dict()),
#         content_type='application/json',
#     )

#     user = MagicMock()
#     user.is_authenticated = True
#     user.is_staff = False
#     request.user = user

#     response = view.dispatch(request)

#     assert response.status_code == 403


# @pytest.mark.django_db
# def test_dispatch_rejects_unauthenticated(
#     factory: RequestFactory,
#     view: SyncView,
# ) -> None:
#     request = factory.post(
#         '/sync/',
#         data=b'{}',
#         content_type='application/json',
#     )

#     user = MagicMock()
#     user.is_authenticated = False
#     request.user = user

#     response = view.dispatch(request)

#     assert response.status_code == 401


# @pytest.mark.django_db
# def test_post_handles_gzip_request(
#     factory: RequestFactory,
#     view: SyncView,
# ) -> None:
#     manifest = SyncManifest(
#         node_id='tablet',
#         checkpoint=0,
#         node_time=100,
#         payloads=[],
#     )

#     request = _make_staff_request(
#         factory,
#         manifest.to_dict(),
#         content_encoding='gzip',
#     )

#     response = view.post(request)

#     assert response.status_code == 200

#     data = json.loads(response.content)

#     assert data['ok'] is True


# @pytest.mark.django_db
# def test_post_rejects_oversized_request(
#     factory: RequestFactory,
#     mock_engine: MagicMock,
# ) -> None:
#     v = SyncView()
#     v.engine = mock_engine
#     v.request_bytes_max = 10

#     request = factory.post(
#         '/sync/',
#         data=b'x' * 100,
#         content_type='application/json',
#     )

#     user = MagicMock()
#     user.is_authenticated = True
#     user.is_staff = True
#     request.user = user

#     response = v.post(request)

#     assert response.status_code == 413


# @pytest.mark.django_db
# def test_post_rejects_oversized_content_length_header(
#     factory: RequestFactory,
#     mock_engine: MagicMock,
# ) -> None:
#     v = SyncView()
#     v.engine = mock_engine
#     v.request_bytes_max = 10

#     request = factory.post(
#         '/sync/',
#         data=b'x' * 5,
#         content_type='application/json',
#     )
#     request.META['CONTENT_LENGTH'] = '9999999'

#     user = MagicMock()
#     user.is_authenticated = True
#     user.is_staff = True
#     request.user = user

#     response = v.post(request)

#     assert response.status_code == 413


# @pytest.mark.django_db
# def test_post_rejects_invalid_content_length_header(
#     factory: RequestFactory,
#     mock_engine: MagicMock,
# ) -> None:
#     v = SyncView()
#     v.engine = mock_engine

#     request = factory.post(
#         '/sync/',
#         data=b'{}',
#         content_type='application/json',
#     )
#     request.META['CONTENT_LENGTH'] = 'not-a-number'

#     user = MagicMock()
#     user.is_authenticated = True
#     user.is_staff = True
#     request.user = user

#     response = v.post(request)

#     assert response.status_code == 400
