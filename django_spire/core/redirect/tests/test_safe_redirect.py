from __future__ import annotations

from django.test import override_settings, RequestFactory

from django_spire.core.redirect.safe_redirect import (
    is_url_valid_and_safe,
    resolve_url,
    safe_redirect_url
)
from django_spire.core.tests.test_cases import BaseTestCase


class UrlsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

    # def test_resolve_valid_url(self) -> None:
    #     valid_url = 'dummy:home'
    #     resolved_url = resolve_url(valid_url)
    #     self.assertEqual(resolved_url, reverse(valid_url))

    def test_is_url_valid_and_safe_empty_url(self) -> None:
        assert is_url_valid_and_safe('', {'localhost'}) is False

    def test_is_url_valid_and_safe_invalid_host(self) -> None:
        url = 'http://invalid.com'

        assert is_url_valid_and_safe(url, {'example.com'}) is False

    def test_is_url_valid_and_safe_invalid_scheme(self) -> None:
        url = 'ftp://example.com'

        assert is_url_valid_and_safe(url, {'example.com'}) is False

    def test_is_url_valid_and_safe_valid_url(self) -> None:
        url = 'http://example.com'

        assert is_url_valid_and_safe(url, {'example.com'}) is True

    def test_resolve_invalid_url(self) -> None:
        invalid_url = 'invalid:url'
        resolved_url = resolve_url(invalid_url)
        assert resolved_url == invalid_url


@override_settings(ALLOWED_HOSTS=['example.com'])
class ReturnUrlTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.request_factory = RequestFactory()

    def test_safe_redirect_url_invalid_return_url(self) -> None:
        request = self.request_factory.get(
            '/some_path',
            {'return_url': 'http://invalid.com'}
        )

        request.META['HTTP_HOST'] = 'example.com'
        response = safe_redirect_url(request)
        assert response == '/'

    def test_safe_redirect_url_return_url_with_encoded_characters(self) -> None:
        request = self.request_factory.get(
            '/some_path',
            {'return_url': 'http://example.com/valid%20path'}
        )

        request.META['HTTP_HOST'] = 'example.com'
        response = safe_redirect_url(request)
        assert response == 'http://example.com/valid%20path'

    def test_safe_redirect_url_return_url_with_invalid_characters(self) -> None:
        request = self.request_factory.get(
            '/some_path',
            {'return_url': 'http://example.com/invalid<>chars'}
        )

        request.META['HTTP_HOST'] = 'example.com'
        response = safe_redirect_url(request)
        assert response == '/'

    def test_safe_redirect_url_return_url_with_javascript_code(self) -> None:
        request = self.request_factory.get(
            '/some_path',
            {'return_url': 'javascript:alert("XSS")'}
        )

        request.META['HTTP_HOST'] = 'example.com'
        response = safe_redirect_url(request)
        assert response == '/'

    def test_safe_redirect_url_return_url_with_utf8_characters(self) -> None:
        request = self.request_factory.get(
            '/some_path',
            {'return_url': 'http://example.com/ümlaut'}
        )

        request.META['HTTP_HOST'] = 'example.com'
        response = safe_redirect_url(request)
        assert response == 'http://example.com/ümlaut'

    def test_safe_redirect_url_valid_return_url(self) -> None:
        request = self.request_factory.get(
            '/some_path',
            {'return_url': 'http://example.com/valid'}
        )

        request.META['HTTP_HOST'] = 'example.com'
        response = safe_redirect_url(request)
        assert response == 'http://example.com/valid'


@override_settings(ALLOWED_HOSTS=['example.com'])
class RefererTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.request_factory = RequestFactory()

    def test_safe_redirect_url_invalid_referer(self) -> None:
        request = self.request_factory.get('/some_path')
        request.META['HTTP_HOST'] = 'example.com'
        request.META['HTTP_REFERER'] = 'http://invalid.com'

        response = safe_redirect_url(request)
        assert response == '/'

    def test_safe_redirect_url_invalid_return_url(self) -> None:
        request = self.request_factory.get(
            '/some_path',
            {'return_url': 'http://invalid.com'}
        )

        request.META['HTTP_HOST'] = 'example.com'
        response = safe_redirect_url(request)
        assert response == '/'

    def test_safe_redirect_url_no_return_url_or_referer(self) -> None:
        request = self.request_factory.get('/some_path')
        request.META['HTTP_HOST'] = 'example.com'

        response = safe_redirect_url(request)
        assert response == '/'

    def test_safe_redirect_url_referer_with_encoded_characters(self) -> None:
        request = self.request_factory.get('/some_path')
        request.META['HTTP_HOST'] = 'example.com'
        request.META['HTTP_REFERER'] = 'http://example.com/valid%20path'

        response = safe_redirect_url(request)
        assert response == 'http://example.com/valid%20path'

    def test_safe_redirect_url_referer_with_invalid_characters(self) -> None:
        request = self.request_factory.get('/some_path')
        request.META['HTTP_HOST'] = 'example.com'
        request.META['HTTP_REFERER'] = 'http://example.com/invalid<>chars'

        response = safe_redirect_url(request)
        assert response == '/'

    def test_safe_redirect_url_referer_with_javascript_code(self) -> None:
        request = self.request_factory.get('/some_path')
        request.META['HTTP_HOST'] = 'example.com'
        request.META['HTTP_REFERER'] = 'javascript:alert("XSS")'

        response = safe_redirect_url(request)
        assert response == '/'

    def test_safe_redirect_url_referer_with_utf8_characters(self) -> None:
        request = self.request_factory.get('/some_path')
        request.META['HTTP_HOST'] = 'example.com'
        request.META['HTTP_REFERER'] = 'http://example.com/ümlaut'

        response = safe_redirect_url(request)
        assert response == 'http://example.com/ümlaut'

    def test_safe_redirect_url_valid_referer(self) -> None:
        request = self.request_factory.get('/some_path')
        request.META['HTTP_HOST'] = 'example.com'
        request.META['HTTP_REFERER'] = 'http://example.com/valid'

        response = safe_redirect_url(request)
        assert response == 'http://example.com/valid'

    def test_safe_redirect_url_valid_return_url(self) -> None:
        request = self.request_factory.get(
            '/some_path',
            {'return_url': 'http://example.com/valid'}
        )

        request.META['HTTP_HOST'] = 'example.com'
        response = safe_redirect_url(request)
        assert response == 'http://example.com/valid'
