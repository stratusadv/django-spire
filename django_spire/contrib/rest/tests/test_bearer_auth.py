"""
Tests for BearerAuth authentication.
"""

from unittest.mock import Mock

from django.test import TestCase

from django_spire.contrib.rest.connector.auth.bearer import BearerAuth


class TestBearerAuth(TestCase):
    """Tests for BearerAuth class."""

    def test_bearer_auth_adds_authorization_header(self):
        """Test that BearerAuth adds Authorization header."""
        auth = BearerAuth('my-secret-token')

        # Create mock request
        mock_request = Mock()
        mock_request.headers = {}

        # Apply auth
        result = auth(mock_request)

        assert mock_request.headers['Authorization'] == 'Bearer my-secret-token'
        assert result is mock_request

    def test_bearer_auth_default_header_name(self):
        """Test that default header name is 'Authorization'."""
        assert BearerAuth.auth_header_name == 'Authorization'

    def test_bearer_auth_custom_header_name(self):
        """Test that custom header name can be used."""

        class CustomBearerAuth(BearerAuth):
            auth_header_name = 'X-Auth-Token'

        auth = CustomBearerAuth('my-secret-token')

        mock_request = Mock()
        mock_request.headers = {}

        auth(mock_request)

        assert 'X-Auth-Token' in mock_request.headers
        assert mock_request.headers['X-Auth-Token'] == 'Bearer my-secret-token'

    def test_bearer_auth_preserves_existing_headers(self):
        """Test that existing headers are preserved."""
        auth = BearerAuth('token')

        mock_request = Mock()
        mock_request.headers = {'Content-Type': 'application/json'}

        auth(mock_request)

        assert mock_request.headers['Content-Type'] == 'application/json'
        assert mock_request.headers['Authorization'] == 'Bearer token'
