from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

import pytest

from django_spire.auth.controller.controller import AppAuthController, BaseAuthController
from django_spire.auth.controller.exceptions import (
    AuthControllerNotFoundError,
    AuthControllerRequestError,
)
from django_spire.auth.user.tests.factories import create_super_user, create_user
from django_spire.core.tests.test_cases import BaseTestCase

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


class TestAuthController(BaseAuthController):
    condition: bool = True

    def also_can_access(self) -> bool:
        return True

    def can_access(self) -> bool:
        return True

    def cannot_access(self) -> bool:
        return False

    def conditional_access(self) -> bool:
        return self.condition

    def request_based_access(self) -> bool:
        return self.request.user.is_authenticated


class BaseAuthControllerTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()
        self.user = create_user(username='testuser')
        self.controller = BaseAuthController()

    def test_init_without_request(self) -> None:
        controller = BaseAuthController()
        assert controller._request is None

    def test_init_with_request(self) -> None:
        request = self.factory.get('/test/')
        controller = BaseAuthController(request=request)
        assert controller._request == request

    def test_request_property_raises_when_none(self) -> None:
        controller = BaseAuthController()
        with pytest.raises(AuthControllerRequestError) as exc_info:
            _ = controller.request
        assert 'None' in str(exc_info.value)

    def test_request_setter(self) -> None:
        controller = BaseAuthController()
        request = self.factory.get('/test/')
        controller.request = request
        assert controller.request == request

    def test_request_setter_multiple_times(self) -> None:
        controller = BaseAuthController()
        request1 = self.factory.get('/test1/')
        request2 = self.factory.get('/test2/')
        controller.request = request1
        controller.request = request2
        assert controller.request == request2

    def test_request_property_returns_same_request(self) -> None:
        request = self.factory.get('/test/')
        controller = BaseAuthController(request=request)
        assert controller.request is request

    def test_request_setter_with_none_then_valid(self) -> None:
        controller = BaseAuthController()
        request = self.factory.get('/test/')
        controller._request = None
        controller.request = request
        assert controller.request == request


class BaseAuthControllerPermissionRequiredTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()
        self.user = create_user(username='testuser')
        self.controller = TestAuthController()

    def test_permission_required_with_callable_permission_passes(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result == 'success'

    def test_permission_required_callable_fails(self) -> None:
        @self.controller.permission_required('cannot_access')
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            test_view(request)

    def test_permission_required_any_with_callable(self) -> None:
        @self.controller.permission_required('can_access', 'cannot_access', all_required=False)
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result == 'success'

    def test_permission_required_all_callable_one_fails(self) -> None:
        @self.controller.permission_required('can_access', 'cannot_access', all_required=True)
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            test_view(request)

    def test_permission_required_sets_request(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        test_view(request)
        assert self.controller.request == request

    def test_permission_required_preserves_function_name(self) -> None:
        @self.controller.permission_required('can_access')
        def my_special_view(_request: WSGIRequest) -> str:
            return 'success'

        assert my_special_view.__name__ == 'my_special_view'

    def test_permission_required_with_args(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(_request: WSGIRequest, arg1: str, arg2: str) -> str:
            return f'{arg1}-{arg2}'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request, 'hello', 'world')
        assert result == 'hello-world'

    def test_permission_required_with_kwargs(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(_request: WSGIRequest, **kwargs) -> str:
            return kwargs.get('key', 'default')

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request, key='value')
        assert result == 'value'

    def test_multiple_callable_permissions_all_pass(self) -> None:
        @self.controller.permission_required('can_access', 'also_can_access', all_required=True)
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result == 'success'

    def test_conditional_permission(self) -> None:
        @self.controller.permission_required('conditional_access')
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        self.controller.condition = True
        result = test_view(request)
        assert result == 'success'

    def test_conditional_permission_fails(self) -> None:
        self.controller.condition = False

        @self.controller.permission_required('conditional_access')
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            test_view(request)

    def test_permission_required_with_mixed_args_kwargs(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(_request: WSGIRequest, arg1: str, kwarg1: str | None = None) -> str:
            return f'{arg1}-{kwarg1}'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request, 'positional', kwarg1='keyword')
        assert result == 'positional-keyword'

    def test_permission_required_callable_uses_request(self) -> None:
        @self.controller.permission_required('request_based_access')
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result == 'success'

    def test_permission_required_with_string_permission_fallback(self) -> None:
        @self.controller.permission_required('nonexistent_method', all_required=True)
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            test_view(request)

    def test_permission_required_superuser_string_permission(self) -> None:
        superuser = create_super_user()

        @self.controller.permission_required('some.fake_permission')
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = superuser
        result = test_view(request)
        assert result == 'success'

    def test_permission_required_empty_permissions(self) -> None:
        @self.controller.permission_required()
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result == 'success'

    def test_permission_required_any_all_fail(self) -> None:
        @self.controller.permission_required('cannot_access', all_required=False)
        def test_view(_request: WSGIRequest) -> str:
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            test_view(request)

    def test_permission_required_view_returns_none(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(_request: WSGIRequest) -> None:
            return None

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result is None

    def test_permission_required_view_returns_complex_object(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(_request: WSGIRequest) -> dict:
            return {'key': 'value', 'list': [1, 2, 3]}

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result == {'key': 'value', 'list': [1, 2, 3]}


class AppAuthControllerTestCase(BaseTestCase):
    def test_app_controller_not_found_raises_error(self) -> None:
        with pytest.raises(AuthControllerNotFoundError):
            AppAuthController('nonexistent_app')

    def test_app_controller_not_found_error_message(self) -> None:
        with pytest.raises(AuthControllerNotFoundError) as exc_info:
            AppAuthController('nonexistent_app')

        assert 'nonexistent_app' in str(exc_info.value)


class AuthControllerExceptionsTestCase(BaseTestCase):
    def test_auth_controller_request_error_is_exception(self) -> None:
        assert issubclass(AuthControllerRequestError, Exception)

    def test_auth_controller_not_found_error_is_exception(self) -> None:
        assert issubclass(AuthControllerNotFoundError, Exception)

    def test_auth_controller_request_error_message(self) -> None:
        error = AuthControllerRequestError('Custom message')
        assert str(error) == 'Custom message'

    def test_auth_controller_not_found_error_message(self) -> None:
        error = AuthControllerNotFoundError('App not found')
        assert str(error) == 'App not found'
