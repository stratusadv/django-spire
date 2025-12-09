from __future__ import annotations

import pytest

from typing import TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

from django_spire.auth.permissions.decorators import (
    permission_required,
    permission_required_decorator_function,
)
from django_spire.auth.user.tests.factories import create_super_user, create_user
from django_spire.core.tests.test_cases import BaseTestCase

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


class PermissionRequiredDecoratorFunctionTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()
        self.user = create_user(username='testuser')
        self.user.set_password('password')
        self.user.save()

    def test_unauthenticated_user_redirects(self) -> None:
        request = self.factory.get('/test/')
        request.user = type('AnonymousUser', (), {'is_authenticated': False})()

        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        response = permission_required_decorator_function(
            'some.permission',
            dummy_view,
            request
        )
        assert response.status_code == 302

    def test_user_without_permission_raises_denied(self) -> None:
        request = self.factory.get('/test/')
        request.user = self.user

        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        with pytest.raises(PermissionDenied):
            permission_required_decorator_function(
                'some.nonexistent_permission',
                dummy_view,
                request
            )

    def test_superuser_has_all_permissions(self) -> None:
        superuser = create_super_user()
        request = self.factory.get('/test/')
        request.user = superuser

        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        result = permission_required_decorator_function(
            'any.permission',
            dummy_view,
            request
        )
        assert result == 'success'

    def test_redirects_to_login(self) -> None:
        request = self.factory.get('/test/')
        request.user = type('AnonymousUser', (), {'is_authenticated': False})()

        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        response = permission_required_decorator_function(
            'some.permission',
            dummy_view,
            request
        )
        assert 'login' in response.url.lower()

    def test_multiple_permissions_all_required(self) -> None:
        request = self.factory.get('/test/')
        request.user = self.user

        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        with pytest.raises(PermissionDenied):
            permission_required_decorator_function(
                ['perm1', 'perm2'],
                dummy_view,
                request,
                all_required=True
            )

    def test_multiple_permissions_any_required(self) -> None:
        superuser = create_super_user()
        request = self.factory.get('/test/')
        request.user = superuser

        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        result = permission_required_decorator_function(
            ['perm1', 'perm2'],
            dummy_view,
            request,
            all_required=False
        )
        assert result == 'success'

    def test_passes_args_to_view(self) -> None:
        superuser = create_super_user()
        request = self.factory.get('/test/')
        request.user = superuser

        def dummy_view(_request: WSGIRequest, arg1: str, arg2: str) -> str:
            return f'{arg1}-{arg2}'

        result = permission_required_decorator_function(
            'any.permission',
            dummy_view,
            request,
            'hello',
            'world'
        )
        assert result == 'hello-world'

    def test_passes_kwargs_to_view(self) -> None:
        superuser = create_super_user()
        request = self.factory.get('/test/')
        request.user = superuser

        def dummy_view(_request: WSGIRequest, **kwargs) -> str:
            return kwargs.get('key', 'default')

        result = permission_required_decorator_function(
            'any.permission',
            dummy_view,
            request,
            key='value'
        )
        assert result == 'value'

    def test_single_permission_as_string(self) -> None:
        superuser = create_super_user()
        request = self.factory.get('/test/')
        request.user = superuser

        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        result = permission_required_decorator_function(
            'single.permission',
            dummy_view,
            request
        )
        assert result == 'success'

    def test_empty_permissions_list(self) -> None:
        request = self.factory.get('/test/')
        request.user = self.user

        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        result = permission_required_decorator_function(
            [],
            dummy_view,
            request
        )
        assert result == 'success'


class PermissionRequiredDecoratorTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()
        self.user = create_user(username='testuser')
        self.user.set_password('password')
        self.user.save()

    def test_decorator_without_permission(self) -> None:
        @permission_required('django_spire_auth_group.delete_authgroup')
        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            dummy_view(request)

    def test_decorator_superuser_succeeds(self) -> None:
        superuser = create_super_user()

        @permission_required('any.permission')
        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = superuser
        result = dummy_view(request)
        assert result == 'success'

    def test_decorator_multiple_permissions_all_required_fails(self) -> None:
        @permission_required(
            'django_spire_auth_group.view_authgroup',
            'django_spire_auth_group.change_authgroup',
            all_required=True
        )
        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            dummy_view(request)

    def test_decorator_preserves_function_name(self) -> None:
        @permission_required('any.permission')
        def my_special_view(_request: WSGIRequest) -> str:
            return 'success'

        assert my_special_view.__name__ == 'my_special_view'

    def test_decorator_with_args(self) -> None:
        superuser = create_super_user()

        @permission_required('any.permission')
        def dummy_view(_request: WSGIRequest, arg1: str, arg2: str) -> str:
            return f'{arg1}-{arg2}'

        request = self.factory.get('/test/')
        request.user = superuser
        result = dummy_view(request, 'hello', 'world')
        assert result == 'hello-world'

    def test_decorator_with_kwargs(self) -> None:
        superuser = create_super_user()

        @permission_required('any.permission')
        def dummy_view(_request: WSGIRequest, **kwargs) -> str:
            return kwargs.get('key', 'default')

        request = self.factory.get('/test/')
        request.user = superuser
        result = dummy_view(request, key='value')
        assert result == 'value'

    def test_decorator_multiple_permissions_any_required_superuser(self) -> None:
        superuser = create_super_user()

        @permission_required('perm1', 'perm2', all_required=False)
        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = superuser
        result = dummy_view(request)
        assert result == 'success'

    def test_decorator_empty_permissions(self) -> None:
        @permission_required()
        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        result = dummy_view(request)
        assert result == 'success'

    def test_decorator_unauthenticated_redirects(self) -> None:
        @permission_required('any.permission')
        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = type('AnonymousUser', (), {'is_authenticated': False})()

        response = dummy_view(request)
        assert response.status_code == 302

    def test_decorator_view_returns_none(self) -> None:
        superuser = create_super_user()

        @permission_required('any.permission')
        def dummy_view(_request: WSGIRequest) -> None:
            return None

        request = self.factory.get('/test/')
        request.user = superuser
        result = dummy_view(request)
        assert result is None

    def test_decorator_view_returns_dict(self) -> None:
        superuser = create_super_user()

        @permission_required('any.permission')
        def dummy_view(_request: WSGIRequest) -> dict:
            return {'key': 'value'}

        request = self.factory.get('/test/')
        request.user = superuser
        result = dummy_view(request)
        assert result == {'key': 'value'}

    def test_decorator_single_permission_denied(self) -> None:
        @permission_required('nonexistent.permission')
        def dummy_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            dummy_view(request)

    def test_decorator_callable_preserves_docstring(self) -> None:
        @permission_required('any.permission')
        def dummy_view(_request: WSGIRequest) -> str:
            """A docstring."""
            return 'success'

        assert dummy_view.__doc__ == 'A docstring.'
