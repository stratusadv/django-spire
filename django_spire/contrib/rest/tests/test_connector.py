"""
Tests for BaseRestHttpConnector.
"""
from unittest.mock import patch, Mock

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from django_spire.contrib.rest import BaseRestHttpConnector


class TestBaseRestHttpConnector(TestCase):
    """Tests for BaseRestHttpConnector base class."""

    def test_base_url_required(self):
        """Test that base_url is required."""
        with self.assertRaises(ImproperlyConfigured) as context:
            class InvalidConnector(BaseRestHttpConnector):
                pass

        self.assertIn('base_url', str(context.exception))

    def test_url_validation_invalid_url(self):
        """Test that invalid URLs raise ValueError."""
        with self.assertRaises(ValueError) as context:
            class InvalidUrlConnector(BaseRestHttpConnector):
                base_url = 'not-a-valid-url'

        self.assertIn('Invalid URL', str(context.exception))

    def test_url_validation_missing_scheme(self):
        """Test that URLs without scheme raise ValueError."""
        with self.assertRaises(ValueError):
            class NoSchemeConnector(BaseRestHttpConnector):
                base_url = 'example.com/api'

    def test_valid_connector_creation(self):
        """Test that valid connectors can be created."""
        class ValidConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'

        connector = ValidConnector()
        self.assertEqual(connector.base_url, 'https://api.example.com')

    def test_build_url_base_only(self):
        """Test URL building with base_url only."""
        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'

        connector = TestConnector()
        url = connector._build_url()

        self.assertEqual(url, 'https://api.example.com')

    def test_build_url_with_path(self):
        """Test URL building with path."""
        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'

        connector = TestConnector()
        url = connector._build_url('users')

        self.assertEqual(url, 'https://api.example.com/users')

    def test_build_url_with_base_path(self):
        """Test URL building with base_path."""
        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'
            base_path = 'v1'

        connector = TestConnector()
        url = connector._build_url('users')

        self.assertEqual(url, 'https://api.example.com/v1/users')

    def test_build_url_strips_slashes(self):
        """Test that path slashes are stripped."""
        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'

        connector = TestConnector()
        url = connector._build_url('/users/')

        self.assertEqual(url, 'https://api.example.com/users')

    def test_default_timeout(self):
        """Test default timeout value."""
        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'

        connector = TestConnector()

        self.assertEqual(connector.timeout, 30)

    def test_custom_timeout(self):
        """Test custom timeout value."""
        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'
            timeout = 60

        connector = TestConnector()

        self.assertEqual(connector.timeout, 60)

    def test_default_auth_returns_none(self):
        """Test that default auth property returns None."""
        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'

        connector = TestConnector()

        self.assertIsNone(connector.auth)

    @patch('requests.request')
    def test_get_request(self, mock_request):
        """Test GET request method."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'

        connector = TestConnector()
        response = connector.get('users')

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args
        self.assertEqual(call_kwargs.kwargs['method'], 'GET')
        self.assertEqual(call_kwargs.kwargs['url'], 'https://api.example.com/users')

    @patch('requests.request')
    def test_request_with_custom_headers(self, mock_request):
        """Test request with custom headers."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'
            base_headers = {'X-Api-Key': 'test-key'}

        connector = TestConnector()
        connector.get('users', headers={'X-Custom': 'value'})

        call_kwargs = mock_request.call_args
        headers = call_kwargs.kwargs['headers']
        self.assertEqual(headers['X-Api-Key'], 'test-key')
        self.assertEqual(headers['X-Custom'], 'value')

    @patch('requests.request')
    def test_post_request(self, mock_request):
        """Test POST request method."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        class TestConnector(BaseRestHttpConnector):
            base_url = 'https://api.example.com'

        connector = TestConnector()
        connector.post('users', json={'name': 'test'})

        call_kwargs = mock_request.call_args
        self.assertEqual(call_kwargs.kwargs['method'], 'POST')
        self.assertEqual(call_kwargs.kwargs['json'], {'name': 'test'})
