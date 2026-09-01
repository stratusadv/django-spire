"""
A permission matrix that audits every named route in a project's URL conf.

This module walks the URL resolver, reads the permission gate declared on
each view, and generates a pytest suite from what it finds: guard tests that
fail when a route escapes the audit, and per-route tests that fire real
requests as anonymous, denied, granted, and superuser actors.

A gate is read from two sources. A spire decorator stamps a `SpireGate` onto
its wrapper, and `functools.wraps` carries the stamp to the outermost wrapper
of any decorator stack, so detection is a single attribute read. A Django
auth decorator (`login_required`, `permission_required`, `user_passes_test`)
stamps nothing, so its gate is recovered by inspecting the closure of the
`user_passes_test` wrapper it is built from. A route with neither shows as
ungated and must be ledgered in `routes_ungated_accepted` to pass the guard test.

The expected denial status follows the gate: a spire gate raises
PermissionDenied (403), a Django gate redirects to the login page (302)
unless it was declared with `raise_exception` (403). A route in
`routes_object_gated` also accepts 404, because an object-level decorator stacked
above the gate fetches its object before the permission check runs and the
matrix fires synthetic URL kwargs that match nothing.

The request fired follows the view too. A decorator that answers requests of
the wrong shape before the gate runs, such as `valid_ajax_request_required`,
stamps a `SpireRequest` onto its wrapper as `__spire_request__`, and the
matrix fires that method and content type from the start so the gate below
it is the one that answers.
"""

from __future__ import annotations

import inspect

from http import HTTPStatus

import pytest

from dataclasses import dataclass
from typing_extensions import TYPE_CHECKING

from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver, reverse
from django.urls.converters import get_converters

from django_spire.auth.user.tests.factories import create_super_user, create_user

if TYPE_CHECKING:
    from typing_extensions import Callable, Iterable, Iterator

    from django.http import HttpResponse
    from django.urls.resolvers import RegexPattern, RoutePattern

    from django_spire.contrib.decorators import SpireRequest


    RouteWalkEntry = tuple[URLPattern, tuple[str, ...], str, tuple[tuple[str, str], ...]]


NAMESPACE_ROOTS_EXCLUDED = frozenset({'admin', 'django_glue', 'django_spire'})

ROUTE_WALK_ENTRY_COUNT_MAX = 10000

KWARG_VALUES_SYNTHETIC = {
    'int': 999999,
    'path': 'synthetic',
    'slug': 'synthetic',
    'str': 'synthetic',
    'uuid': '00000000-0000-0000-0000-000000000000',
}

WRAPPER_CHAIN_LENGTH_MAX = 20

_DJANGO_WRAPPER_FREE_VARIABLES = {'_redirect_to_login', 'test_func'}


@dataclass(frozen=True)
class RouteGate:
    """
    A frozen record of one named route and its effective permission gate.

    :param gated: Whether any gate was detected on the view.
    :param kwargs_specification: The URL kwargs as `(name, converter)` pairs.
    :param name: The fully namespaced route name.
    :param opaque: Whether the gate includes a check the matrix cannot predict.
    :param pattern: The full URL pattern from the resolver root.
    :param permissions: The declared permission labels in `app_label.codename` form.
    :param request_shape: The request shape a decorator above the gate demands, or None for a GET.
    :param statuses_denied: The statuses an authenticated user lacking the permissions may receive.
    """

    gated: bool
    kwargs_specification: tuple[tuple[str, str], ...]
    name: str
    opaque: bool
    pattern: str
    permissions: tuple[str, ...]
    request_shape: SpireRequest | None
    statuses_denied: frozenset[int]


@dataclass(frozen=True)
class _DjangoGate:
    """
    A frozen record of the gate recovered from Django's auth decorators.
    """

    opaque: bool
    permissions: tuple[str, ...]
    statuses_denied: frozenset[int]


def _client_with_permissions(username: str, permission_labels: tuple[str, ...]) -> Client:
    """
    A function that builds a logged-in client holding exactly the given permissions.

    :param username: The username for the created user.
    :param permission_labels: The permission labels in `app_label.codename` form.
    :return: The client with the user logged in.
    """

    user = create_user(username)

    # A label reads 'app_label.codename', the same form the decorators use.
    for label in permission_labels:
        app_label, codename = label.split('.', 1)

        permission = Permission.objects.get(
            codename=codename,
            content_type__app_label=app_label,
        )

        user.user_permissions.add(permission)

    client = Client()
    client.force_login(user)

    return client


def _converter_names_by_type() -> dict[type, str]:
    """
    A function that inverts Django's converter registry into type -> name.

    :return: The mapping from converter class to its registered name.
    """

    # get_converters() holds every converter, custom registered ones
    # included, keyed by the name written inside <name:kwarg> patterns.
    return {type(converter): name for name, converter in get_converters().items()}


def _django_gate_extract(view: Callable) -> _DjangoGate | None:
    """
    A function that recovers the gate declared with Django's auth decorators.

    A Django auth decorator is a `user_passes_test` wrapper, and
    `functools.wraps` overwrites the wrapper's qualname with the view's own,
    so the wrapper is recognized by its closure variables instead: only
    `user_passes_test` produces a function closing over both `test_function` and
    `_redirect_to_login`. The test function's qualname then classifies the
    gate. A `login_required` lambda is a plain login gate, a
    `permission_required` check carries `perms` and `raise_exception` in its
    closure, and any other test function marks the gate opaque because its
    predicate cannot be evaluated from permission labels.

    :param view: The resolved view callable from the URL pattern.
    :return: The recovered gate, or None if no Django auth wrapper is present.
    """

    function = view
    statuses_denied: set[int] = set()
    login_gated = False
    opaque = False
    permissions: list[str] = []

    for _ in range(WRAPPER_CHAIN_LENGTH_MAX):
        if function is None:
            break

        free_variables = (
            set(function.__code__.co_freevars)
            if inspect.isfunction(function)
            else set()
        )

        # Every Django auth decorator wraps the view with user_passes_test.
        # The wrapper's own name is hidden by functools.wraps, but its
        # closure always holds these two variables, so match on those.
        if _DJANGO_WRAPPER_FREE_VARIABLES.issubset(free_variables):
            login_gated = True

            # test_func is the check the decorator runs on each request.
            # Its qualname says which decorator created it.
            test_function = inspect.getclosurevars(function).nonlocals.get('test_func')
            test_function_qualname = getattr(test_function, '__qualname__', '')

            is_login_check = test_function_qualname.startswith('login_required.')
            is_permission_check = test_function_qualname.startswith('permission_required.')

            if is_permission_check:
                # The declared permissions sit in the check's closure:
                # `perms` on current Django, `perm` on older releases.
                test_closure = inspect.getclosurevars(test_function).nonlocals
                declared = test_closure.get('perms') or test_closure.get('perm') or ()

                # The decorator accepts one label or a list of labels.
                if isinstance(declared, str):
                    permissions.append(declared)
                else:
                    permissions.extend(declared)

                # raise_exception=True answers 403; the default redirects
                # to the login page (302).
                if test_closure.get('raise_exception'):
                    statuses_denied.add(HTTPStatus.FORBIDDEN)
                else:
                    statuses_denied.add(HTTPStatus.FOUND)

            if not is_login_check and not is_permission_check:
                # A custom check we cannot predict, so only the anonymous
                # test runs against this route.
                opaque = True

        function = getattr(function, '__wrapped__', None)

    if not login_gated:
        return None

    return _DjangoGate(
        opaque=opaque,
        permissions=tuple(permissions),
        statuses_denied=frozenset(statuses_denied),
    )


def _namespace_audited(
    namespace_parts: tuple[str, ...],
    namespaces: frozenset[str] | None,
) -> bool:
    """
    A function that decides whether a route's namespace is inside the audit.

    :param namespace_parts: The namespace chain from the resolver root.
    :param namespaces: The audited root namespaces, or None for all but the exclusions.
    :return: True if the route is audited, False otherwise.
    """

    root = namespace_parts[0] if namespace_parts else ''

    if namespaces is None:
        return root not in NAMESPACE_ROOTS_EXCLUDED

    return root in namespaces


def _pattern_kwargs_read(
    pattern: RegexPattern | RoutePattern,
    converter_names: dict[type, str],
) -> tuple[tuple[str, str], ...]:
    """
    A function that reads a pattern's URL kwargs from Django's own data.

    Django stores each path() kwarg with its converter on the pattern
    object, so no string parsing is needed. A re_path() kwarg is a plain
    regex group with no converter and defaults to `str`.

    :param pattern: The pattern object from a URL entry or resolver.
    :param converter_names: The mapping from converter class to registered name.
    :return: The `(name, converter)` pairs.
    """

    # Every path() kwarg sits in pattern.converters with its converter.
    kwargs = [
        (kwarg_name, converter_names.get(type(converter), 'str'))
        for kwarg_name, converter in pattern.converters.items()
    ]

    # A re_path() kwarg only appears as a named group in the regex.
    for kwarg_name in pattern.regex.groupindex:
        if kwarg_name not in pattern.converters:
            kwarg = (kwarg_name, 'str')
            kwargs.append(kwarg)

    return tuple(kwargs)


def _route_fire(
    client: Client,
    route: RouteGate,
    kwarg_values: dict[str, object] | None = None,
) -> HttpResponse:
    """
    A function that fires one request at a route with synthetic URL kwargs.

    The request is a GET unless the route declares a request shape, in which
    case the declared method and content type are fired from the start. A
    view that only accepts other methods answers 405 and names them in its
    Allow header, so the request is refired with the first method the view
    accepts, and no method decorator is inspected.

    :param client: The client carrying the actor under test.
    :param route: The route to fire.
    :param kwarg_values: The synthetic value per converter name, defaulting
        to `KWARG_VALUES_SYNTHETIC`.
    :return: The response from the view.
    """

    if kwarg_values is None:
        kwarg_values = KWARG_VALUES_SYNTHETIC

    # Every URL kwarg gets a throwaway value matching its converter, so the
    # URL reverses cleanly and points at a record that does not exist.
    url_kwargs = {
        name: kwarg_values.get(converter, 'synthetic')
        for name, converter in route.kwargs_specification
    }

    url = reverse(route.name, kwargs=url_kwargs)

    if route.request_shape is None:
        response = client.get(url)
    else:
        # A decorator above the gate answers any other shape itself, before
        # the gate runs, so the declared shape is what reaches the gate.
        response = client.generic(
            route.request_shape.method,
            url,
            data='{}',
            content_type=route.request_shape.content_type,
        )

    if response.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
        # The Allow header lists what the view accepts, such as 'POST,
        # OPTIONS'. Pick the first real method from it.
        methods = [
            method.strip()
            for method in response.headers.get('Allow', 'POST').split(',')
        ]
        method = next(
            (method for method in methods if method not in ('HEAD', 'OPTIONS')),
            'POST',
        )

        response = client.generic(method, url)

    return response


def _route_gate_build(
    callback: Callable,
    kwargs_specification: tuple[tuple[str, str], ...],
    name: str,
    pattern: str,
) -> RouteGate:
    """
    A function that merges a view's spire and Django gates into one record.

    A view can carry both gates at once, such as `login_required` stacked
    over a spire `permission_required`, so the denied statuses are the union
    of what each gate produces and the permissions concatenate.

    :param callback: The resolved view callable from the URL pattern.
    :param kwargs_specification: The URL kwargs as `(name, converter)` pairs.
    :param name: The fully namespaced route name.
    :param pattern: The full URL pattern from the resolver root.
    :return: The merged route record.
    """

    spire_gate = getattr(callback, '__spire_gate__', None)
    django_gate = _django_gate_extract(callback)
    request_shape = getattr(callback, '__spire_request__', None)

    statuses_denied: set[int] = set()
    opaque = False
    permissions: list[str] = []

    # A spire gate always answers 403 when permissions are missing.
    if spire_gate is not None:
        opaque = opaque or spire_gate.opaque

        permissions.extend(spire_gate.permissions)

        if spire_gate.permissions:
            statuses_denied.add(HTTPStatus.FORBIDDEN)

    # A Django gate brings its own denial status: 302 in redirect mode,
    # 403 when declared with raise_exception.
    if django_gate is not None:
        statuses_denied |= django_gate.statuses_denied
        opaque = opaque or django_gate.opaque

        permissions.extend(django_gate.permissions)

    return RouteGate(
        gated=spire_gate is not None or django_gate is not None,
        kwargs_specification=kwargs_specification,
        name=name,
        opaque=opaque,
        pattern=pattern,
        permissions=tuple(permissions),
        request_shape=request_shape,
        statuses_denied=frozenset(statuses_denied),
    )


def _routes_collect(
    namespaces: frozenset[str] | None,
) -> tuple[tuple[RouteGate, ...], tuple[tuple[str, str], ...]]:
    """
    A function that collects every audited route and every unnamed pattern.

    :param namespaces: The audited root namespaces, or None for all but the exclusions.
    :return: The sorted routes and the sorted `(namespace, pattern)` pairs lacking a name.
    """

    routes: list[RouteGate] = []
    patterns_unnamed: list[tuple[str, str]] = []

    for entry, namespace_parts, pattern_prefix, kwargs_specification in _url_patterns_walk():
        # A route outside the audited namespaces is someone else's problem.
        if not _namespace_audited(namespace_parts, namespaces):
            continue

        pattern_full = pattern_prefix + str(entry.pattern)

        # A route without a name cannot be reversed or tested, so it goes
        # to the guard test that demands every route be named.
        if not entry.name:
            pattern_unnamed = (':'.join(namespace_parts), pattern_full)

            patterns_unnamed.append(pattern_unnamed)

            continue

        route = _route_gate_build(
            entry.callback,
            kwargs_specification,
            ':'.join((*namespace_parts, entry.name)),
            pattern_full,
        )

        routes.append(route)

    routes_sorted = tuple(sorted(routes, key=lambda route: route.name))

    return routes_sorted, tuple(sorted(patterns_unnamed))


def _superuser_client() -> Client:
    """
    A function that builds a logged-in superuser client.

    :return: The client with the superuser logged in.
    """

    user = create_super_user()

    client = Client()
    client.force_login(user)

    return client


def _url_patterns_walk() -> Iterator[RouteWalkEntry]:
    """
    A function that walks the URL resolver tree iteratively.

    The walk is bounded by `ROUTE_WALK_ENTRY_COUNT_MAX` so a cyclic or
    pathological resolver fails loudly instead of hanging the collection.
    Each yielded route carries the URL kwargs gathered along its whole path,
    because an include prefix can declare kwargs of its own.

    :return: An iterator of `(pattern, namespace_parts, pattern_prefix, kwargs)` tuples.
    :raises RuntimeError: If the walk exceeds its entry bound.
    """

    stack: list[tuple[object, tuple[str, ...], str, tuple[tuple[str, str], ...]]] = [
        (entry, (), '', ())
        for entry in get_resolver().url_patterns
    ]

    converter_names = _converter_names_by_type()
    entry_count = 0

    while stack:
        entry_count += 1

        if entry_count > ROUTE_WALK_ENTRY_COUNT_MAX:
            message = f'route walk exceeded bound of {ROUTE_WALK_ENTRY_COUNT_MAX} entries'
            raise RuntimeError(message)

        entry, namespace_parts, pattern_prefix, kwargs_inherited = stack.pop()

        # An include: push its children and keep walking. The children
        # inherit any kwargs the include's own prefix declares, such as an
        # include mounted at 'company/<slug:company_slug>/'.
        if isinstance(entry, URLResolver):
            namespace_parts_next = (
                (*namespace_parts, entry.namespace)
                if entry.namespace
                else namespace_parts
            )
            kwargs_next = kwargs_inherited + _pattern_kwargs_read(entry.pattern, converter_names)

            stack.extend(
                (child, namespace_parts_next, pattern_prefix + str(entry.pattern), kwargs_next)
                for child in entry.url_patterns
            )

            continue

        if isinstance(entry, URLPattern):
            kwargs_full = kwargs_inherited + _pattern_kwargs_read(entry.pattern, converter_names)

            yield entry, namespace_parts, pattern_prefix, kwargs_full


def matrix_suite(
    namespaces: Iterable[str] | None = None,
    routes_ungated_accepted: Iterable[str] = frozenset(),
    routes_object_gated: Iterable[str] = frozenset(),
    kwarg_values: dict[str, object] | None = None,
) -> type:
    """
    A function that builds the permission matrix suite for the project's URL conf.

    This function collects the audited routes at import time and returns a
    pytest class whose tests are parametrized per route. A project adopts the
    matrix by assigning the result to a `Test`-prefixed name in a test module:

        TestPermissionMatrix = matrix_suite(namespaces={'sales', 'home'})

    :param namespaces: The root namespaces to audit, or None for every namespace
        except `NAMESPACE_ROOTS_EXCLUDED`.
    :param routes_ungated_accepted: The route names accepted without a detectable gate,
        such as public pages or views gated by a custom decorator in the view body.
    :param routes_object_gated: The gated route names whose outermost decorator fetches
        an object before the permission check, so a 404 is accepted where the
        gate would otherwise answer.
    :param kwarg_values: The synthetic URL value per converter name, merged over
        `KWARG_VALUES_SYNTHETIC`; a project with a custom path converter supplies
        a value its regex accepts, keyed by the converter's registered name.
    :return: The pytest suite class.
    """

    namespaces_audited = None if namespaces is None else frozenset(namespaces)
    ledger_ungated = frozenset(routes_ungated_accepted)
    ledger_object = frozenset(routes_object_gated)
    kwarg_values_effective = {**KWARG_VALUES_SYNTHETIC, **(kwarg_values or {})}

    routes, patterns_unnamed = _routes_collect(namespaces_audited)

    # Three shrinking partitions decide which tests a route receives.
    # Gated routes get the anonymous test. Transparent routes (no check the
    # matrix cannot predict) also get the superuser test. Enforced routes
    # (transparent, with declared permissions) get the denied and granted
    # tests as well.
    routes_gated = tuple(route for route in routes if route.gated)
    routes_transparent = tuple(route for route in routes_gated if not route.opaque)
    routes_enforced = tuple(route for route in routes_transparent if route.permissions)

    route_ids_gated = [route.name for route in routes_gated]
    route_ids_transparent = [route.name for route in routes_transparent]
    route_ids_enforced = [route.name for route in routes_enforced]

    @pytest.mark.django_db
    class Suite:
        """
        A pytest suite auditing route permissions for one URL conf.
        """

        def test_declared_permissions_exist(self) -> None:
            """
            A test that fails when a view declares a permission missing from the database.
            """

            declared = {
                label
                for route in routes_gated
                for label in route.permissions
            }

            known_rows = Permission.objects.values_list('content_type__app_label', 'codename')
            known = {f'{app_label}.{codename}' for app_label, codename in known_rows}

            unknown = declared - known

            assert unknown == set(), (
                f'views require permissions that do not exist; the decorator app '
                f'label or codename is wrong: {sorted(unknown)}'
            )

        def test_gated_routes_exist(self) -> None:
            """
            A test that fails when the collection finds no gated routes at all.
            """

            assert routes_gated != (), 'no gated routes collected; the matrix audits nothing'

        def test_object_routes_ledgered_are_gated(self) -> None:
            """
            A test that fails when the object ledger names a route without a gate.
            """

            stale = ledger_object - {route.name for route in routes_gated}

            assert stale == set(), (
                f'object routes are not gated routes; remove them from the '
                f'object ledger: {sorted(stale)}'
            )

        @pytest.mark.parametrize('route', routes_transparent, ids=route_ids_transparent)
        def test_route_admits_superuser(self, route: RouteGate) -> None:
            """
            A test that fails when a superuser is forbidden or the view errors.
            """

            response = _route_fire(_superuser_client(), route, kwarg_values_effective)

            assert response.status_code != HTTPStatus.FORBIDDEN
            assert response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR

        @pytest.mark.parametrize('route', routes_enforced, ids=route_ids_enforced)
        def test_route_admits_user_with_declared_permissions(self, route: RouteGate) -> None:
            """
            A test that fails when the route's own permissions are not enough to enter.
            """

            client = _client_with_permissions('matrix_granted', route.permissions)

            response = _route_fire(client, route, kwarg_values_effective)

            assert response.status_code != HTTPStatus.FORBIDDEN
            assert response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR

        @pytest.mark.parametrize('route', routes_gated, ids=route_ids_gated)
        def test_route_rejects_anonymous(self, route: RouteGate) -> None:
            """
            A test that fails when a gated route answers an anonymous request.
            """

            response = _route_fire(Client(), route, kwarg_values_effective)

            expected = {HTTPStatus.FOUND}

            if route.opaque:
                expected.add(HTTPStatus.FORBIDDEN)

            if route.name in ledger_object:
                expected.add(HTTPStatus.FORBIDDEN)
                expected.add(HTTPStatus.NOT_FOUND)

            assert response.status_code in expected

        @pytest.mark.parametrize('route', routes_enforced, ids=route_ids_enforced)
        def test_route_rejects_user_without_permissions(self, route: RouteGate) -> None:
            """
            A test that fails when a permissionless user is not denied.
            """

            client = _client_with_permissions('matrix_denied', ())

            response = _route_fire(client, route, kwarg_values_effective)

            expected = set(route.statuses_denied)

            if route.name in ledger_object:
                expected.add(HTTPStatus.NOT_FOUND)

            assert response.status_code in expected

        def test_routes_gated_or_ledgered(self) -> None:
            """
            A test that fails when a route has no detectable gate and no ledger entry.
            """

            ungated = {route.name for route in routes if not route.gated}

            missing = ungated - ledger_ungated
            stale = ledger_ungated - ungated

            assert missing == set(), (
                f'routes without a detectable gate; gate them or ledger them in '
                f'routes_ungated_accepted: {sorted(missing)}'
            )

            assert stale == set(), (
                f'ledgered routes are now gated or gone; remove them from '
                f'routes_ungated_accepted: {sorted(stale)}'
            )

        def test_routes_named(self) -> None:
            """
            A test that fails when an audited pattern has no route name.
            """

            formatted = [f'{namespace}: {pattern}' for namespace, pattern in patterns_unnamed]

            assert formatted == [], (
                f'unnamed routes escape the permission matrix; name them: {formatted}'
            )

    return Suite
