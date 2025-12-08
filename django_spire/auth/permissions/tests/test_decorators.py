from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.test import RequestFactory

import pytest

from django_spire.auth.permissions.decorators import (
    permission_required,
    permission_required_decorator_function,
)
from django_spire.auth.user.tests.factories import create_user, create_super_user
from django_spire.core.tests.test_cases import BaseTestCase


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

        def dummy_view(request):
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

        def dummy_view(request):
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

        def dummy_view(request):
            return 'success'

        result = permission_required_decorator_function(
            'any.permission',
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
        def dummy_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            dummy_view(request)

    def test_decorator_superuser_succeeds(self) -> None:
        superuser = create_super_user()

        @permission_required('any.permission')
        def dummy_view(request):
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
        def dummy_view(request):
            return 'success'

        request = self.factory.get('/test/')
        request.user = self.user

        with pytest.raises(PermissionDenied):
            dummy_view(request)
