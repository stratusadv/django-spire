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
from django_spire.core.decorators import valid_ajax_request_required
from django_spire.testing.permissions import _django_gate_extract, matrix_suite

if TYPE_CHECKING:
    from typing_extensions import Callable

    from django.core.handlers.wsgi import WSGIRequest

    from django.http import HttpResponse


HOME_NAMESPACES = frozenset({'home'})

# The detail route stacks example_object_required above its gate, so a 404
# from the synthetic pk is accepted where the gate would otherwise answer.
HOME_ROUTES_OBJECT_GATED = frozenset({'home:page:restricted_detail'})

# The landing page is deliberately public in the test project, so it sits in
# the ungated ledger rather than carrying a gate.
HOME_ROUTES_UNGATED_ACCEPTED = frozenset({'home:page:home'})


def test_controller_gate_marks_callable_permissions_opaque() -> None:
    """
    A test that fails when a controller gate misclassifies its permissions.
    """

    class ExampleAuthController(BaseAuthController):
        def can_view(self) -> bool:
            return True

    controller = ExampleAuthController()

    @controller.permission_required('can_view', 'test_project_home.view_homeexample')
    def view(request: WSGIRequest) -> HttpResponse:
        raise NotImplementedError

    gate = view.__spire_gate__

    assert gate.all_required is True
    assert gate.opaque is True
    assert gate.permissions == ('test_project_home.view_homeexample',)


def test_django_gate_extract_reads_django_decorators() -> None:
    """
    A test that fails when a Django upgrade changes the decorator internals
    the extraction inspects, before any project matrix degrades silently.
    """

    @django_login_required
    def login_view(request: WSGIRequest) -> HttpResponse:
        raise NotImplementedError

    @django_permission_required('test_project_home.view_homeexample')
    def permission_view(request: WSGIRequest) -> HttpResponse:
        raise NotImplementedError

    login_gate = _django_gate_extract(login_view)
    permission_gate = _django_gate_extract(permission_view)

    assert login_gate is not None
    assert login_gate.opaque is False
    assert login_gate.permissions == ()

    assert permission_gate is not None
    assert permission_gate.opaque is False
    assert permission_gate.permissions == ('test_project_home.view_homeexample',)
    assert permission_gate.statuses_denied == frozenset({HTTPStatus.FOUND})


def test_gate_attribute_survives_wrapping_decorator() -> None:
    """
    A test that fails when a wraps-using decorator drops the gate stamp.
    """

    def passthrough(view_func: Callable[..., HttpResponse]) -> Callable[..., HttpResponse]:
        @functools.wraps(view_func)
        def wrapper(request: WSGIRequest, *args, **kwargs) -> HttpResponse:
            return view_func(request, *args, **kwargs)

        return wrapper

    @passthrough
    @permission_required('test_project_home.view_homeexample', all_required=False)
    def view(request: WSGIRequest) -> HttpResponse:
        raise NotImplementedError

    gate = view.__spire_gate__

    assert gate.all_required is False
    assert gate.opaque is False
    assert gate.permissions == ('test_project_home.view_homeexample',)


def test_request_shape_stamp_stacks_over_gate_stamp() -> None:
    """
    A test that fails when a request-shape decorator drops the gate stamp
    below it or fails to stamp its own shape.
    """

    @valid_ajax_request_required
    @permission_required('test_project_home.change_homeexample')
    def view(request: WSGIRequest) -> HttpResponse:
        raise NotImplementedError

    gate = view.__spire_gate__
    shape = view.__spire_request__

    assert gate.permissions == ('test_project_home.change_homeexample',)
    assert shape.content_type == 'application/json'
    assert shape.method == 'POST'


TestHomePermissionMatrix = matrix_suite(
    namespaces=HOME_NAMESPACES,
    routes_ungated_accepted=HOME_ROUTES_UNGATED_ACCEPTED,
    routes_object_gated=HOME_ROUTES_OBJECT_GATED,
)
