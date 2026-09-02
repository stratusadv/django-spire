from __future__ import annotations

import functools

from http import HTTPStatus
from typing_extensions import TYPE_CHECKING

from django.contrib.auth.decorators import (
    login_required as django_login_required,
    permission_required as django_permission_required,
)

from django_spire.auth.controller.controller import BaseAuthController
from django_spire.auth.permissions.decorators import permission_required
from django_spire.contrib.decorators import valid_ajax_request_required
from django_spire.testing.permissions import Gate, PermissionTests

if TYPE_CHECKING:
    from typing_extensions import Callable

    from django.http import HttpRequest, HttpResponse


HOME_NAMESPACES = frozenset({'home'})

# The detail route stacks example_object_required above its gate, so a 404
# from the fake pk is accepted where the gate would otherwise answer.
HOME_OBJECT_ROUTES = frozenset({'home:page:restricted_detail'})

# The demo pages are deliberately public in the test project.
HOME_PUBLIC_ROUTES = frozenset({
    'home:page:chart_demo',
    'home:page:home',
    'home:page:markdown_demo',
})


def test_controller_gate_marks_callable_permissions_as_custom_check() -> None:
    class ExampleAuthController(BaseAuthController):
        def can_view(self) -> bool:
            return True

    controller = ExampleAuthController()

    @controller.permission_required('can_view', 'test_project_home.view_homeexample')
    def view(request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    gate = view.__spire_gate__

    assert gate.all_required is True
    assert gate.has_custom_check is True
    assert gate.permissions == ('test_project_home.view_homeexample',)


def test_gate_from_django_view_reads_django_decorators() -> None:
    @django_login_required
    def login_view(request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    @django_permission_required('test_project_home.view_homeexample')
    def permission_view(request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    @django_permission_required('test_project_home.view_homeexample', raise_exception=True)
    def forbidden_view(request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    def plain_view(request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    login_gate = Gate.from_django_view(login_view)
    permission_gate = Gate.from_django_view(permission_view)
    forbidden_gate = Gate.from_django_view(forbidden_view)

    assert login_gate is not None
    assert login_gate.has_custom_check is False
    assert login_gate.permissions == ()
    assert login_gate.statuses_rejected == frozenset()

    assert permission_gate is not None
    assert permission_gate.has_custom_check is False
    assert permission_gate.permissions == ('test_project_home.view_homeexample',)
    assert permission_gate.statuses_rejected == frozenset({HTTPStatus.FOUND})

    assert forbidden_gate is not None
    assert forbidden_gate.statuses_rejected == frozenset({HTTPStatus.FORBIDDEN})

    assert Gate.from_django_view(plain_view) is None


def test_gate_attribute_survives_wrapping_decorator() -> None:
    def passthrough(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        @functools.wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            return view_func(request, *args, **kwargs)

        return wrapper

    @passthrough
    @permission_required('test_project_home.view_homeexample', all_required=False)
    def view(request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    gate = view.__spire_gate__

    assert gate.all_required is False
    assert gate.has_custom_check is False
    assert gate.permissions == ('test_project_home.view_homeexample',)


def test_request_stamp_stacks_over_gate_stamp() -> None:
    @valid_ajax_request_required
    @permission_required('test_project_home.change_homeexample')
    def view(request: HttpRequest) -> HttpResponse:
        raise NotImplementedError

    gate = view.__spire_gate__
    request = view.__spire_request__

    assert gate.permissions == ('test_project_home.change_homeexample',)
    assert request.content_type == 'application/json'
    assert request.method == 'POST'


class TestHomePermissions(PermissionTests):
    namespaces = HOME_NAMESPACES
    object_routes = HOME_OBJECT_ROUTES
    public_routes = HOME_PUBLIC_ROUTES
