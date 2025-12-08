from __future__ import annotations

import pytest

from unittest.mock import MagicMock, patch

from django.http import HttpRequest, JsonResponse
from django.test import RequestFactory, TestCase

from django_spire.core.decorators import close_db_connections, valid_ajax_request_required


class TestCloseDbConnections(TestCase):
    @patch('django_spire.core.decorators.connections')
    def test_closes_connections_after_exception(self, mock_connections: MagicMock) -> None:
        @close_db_connections
        def sample_func():
            raise ValueError

        with pytest.raises(ValueError):
            sample_func()

        mock_connections.close_all.assert_called_once()

    @patch('django_spire.core.decorators.connections')
    def test_closes_connections_after_success(self, mock_connections: MagicMock) -> None:
        @close_db_connections
        def sample_func():
            return 'result'

        result = sample_func()

        assert result == 'result'
        mock_connections.close_all.assert_called_once()

    @patch('django_spire.core.decorators.connections')
    def test_preserves_function_metadata(self, _mock_connections: MagicMock) -> None:
        @close_db_connections
        def sample_func():
            """Sample docstring"""

        assert sample_func.__name__ == 'sample_func'
        assert sample_func.__doc__ == 'Sample docstring'


class TestValidAjaxRequestRequired(TestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()

    def test_get_request_returns_error(self) -> None:
        @valid_ajax_request_required
        def sample_view(_request: HttpRequest) -> dict:
            return {'success': True}

        request = self.factory.get('/test/')
        response = sample_view(request)

        assert response.status_code == 200
        assert b'error' in response.content

    def test_post_request_with_json_content_type_succeeds(self) -> None:
        @valid_ajax_request_required
        def sample_view(_request: HttpRequest) -> JsonResponse:
            return JsonResponse({'success': True})

        request = self.factory.post(
            '/test/',
            data='{}',
            content_type='application/json'
        )
        response = sample_view(request)

        assert response.status_code == 200
        assert b'success' in response.content

    def test_post_request_without_json_content_type_passes(self) -> None:
        @valid_ajax_request_required
        def sample_view(_request: HttpRequest) -> JsonResponse:
            return JsonResponse({'success': True})

        request = self.factory.post('/test/', data={})
        response = sample_view(request)

        assert response.status_code == 200
        assert b'success' in response.content

    def test_preserves_function_metadata(self) -> None:
        @valid_ajax_request_required
        def sample_view(_request: HttpRequest) -> None:
            """Sample docstring"""

        assert sample_view.__name__ == 'sample_view'
        assert sample_view.__doc__ == 'Sample docstring'
