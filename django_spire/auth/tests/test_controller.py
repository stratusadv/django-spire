from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

import pytest

from django_spire.auth.controller.controller import BaseAuthController
from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase


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
        with pytest.raises(Exception) as exc_info:
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


class BaseAuthControllerPermissionRequiredTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.factory = RequestFactory()
        self.user = create_user(username='testuser')
        self.controller = TestAuthController()

    def test_permission_required_with_callable_permission_passes(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result == 'success'

    def test_permission_required_callable_fails(self) -> None:
        @self.controller.permission_required('cannot_access')
        def test_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            test_view(request)

    def test_permission_required_any_with_callable(self) -> None:
        @self.controller.permission_required('can_access', 'cannot_access', all_required=False)
        def test_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result == 'success'

    def test_permission_required_all_callable_one_fails(self) -> None:
        @self.controller.permission_required('can_access', 'cannot_access', all_required=True)
        def test_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            test_view(request)

    def test_permission_required_sets_request(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        test_view(request)
        assert self.controller.request == request

    def test_permission_required_preserves_function_name(self) -> None:
        @self.controller.permission_required('can_access')
        def my_special_view(request):
            return 'success'

        assert my_special_view.__name__ == 'my_special_view'

    def test_permission_required_with_args(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(request, arg1, arg2):
            return f'{arg1}-{arg2}'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request, 'hello', 'world')
        assert result == 'hello-world'

    def test_permission_required_with_kwargs(self) -> None:
        @self.controller.permission_required('can_access')
        def test_view(request, **kwargs):
            return kwargs.get('key', 'default')

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request, key='value')
        assert result == 'value'

    def test_multiple_callable_permissions_all_pass(self) -> None:
        @self.controller.permission_required('can_access', 'also_can_access', all_required=True)
        def test_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user
        result = test_view(request)
        assert result == 'success'

    def test_conditional_permission(self) -> None:
        @self.controller.permission_required('conditional_access')
        def test_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        self.controller.condition = True
        result = test_view(request)
        assert result == 'success'

    def test_conditional_permission_fails(self) -> None:
        self.controller.condition = False

        @self.controller.permission_required('conditional_access')
        def test_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            test_view(request)


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
