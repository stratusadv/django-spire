"""
Permission tests for every named route in a project's URL conf.

A project subclasses `PermissionTests` and sets three class attributes:

    class TestPermissions(PermissionTests):
        namespaces = {'sales', 'home'}
        object_routes = {'sales:deal:page:detail'}
        public_routes = {'home:page:home'}

The subclass fires a real request at every route as four users: anonymous, a
user without the permission, a user with the permission, and a superuser.
Three one-shot tests guard the surface: every route is named, every route is
protected or listed in `public_routes`, and every declared permission exists.

A view is protected when it carries a spire decorator (`permission_required`,
or a controller's `permission_required`), which stamps a `SpireGate` on the
view, or a Django decorator (`login_required`, `permission_required`,
`user_passes_test`), which is recognised from the closure of the wrapper it
creates. A route in `object_routes` loads its object before the permission
check runs, so a 404 for the fake id is accepted where the gate would answer.
"""

from __future__ import annotations

import inspect
import sysconfig
import traceback

import pytest

from dataclasses import dataclass
from http import HTTPStatus
from typing_extensions import TYPE_CHECKING

from django.conf import settings
from django.contrib.auth.models import Permission
from django.shortcuts import resolve_url
from django.test import Client
from django.urls import URLPattern, URLResolver, get_resolver, reverse
from django.urls.converters import UUIDConverter

from django_spire.auth.user.tests.factories import create_super_user, create_user

if TYPE_CHECKING:
    from types import TracebackType
    from typing_extensions import Callable, Iterable

    from django.http import HttpResponse
    from django.urls.resolvers import RegexPattern, RoutePattern


NAMESPACES_SKIPPED = frozenset({'admin', 'django_glue', 'django_spire'})

PATH_PREFIXES_THIRD_PARTY = tuple(
    sysconfig.get_paths()[name]
    for name in ('platlib', 'purelib', 'stdlib')
)

ROUTE_COUNT_MAX = 10000

URL_VALUE = '999999'
URL_VALUE_UUID = '00000000-0000-0000-0000-000000000000'


@dataclass(frozen=True)
class Gate:
    has_custom_check: bool
    permissions: tuple[str, ...]
    statuses_rejected: frozenset[int]

    @classmethod
    def from_django_view(cls, view: Callable) -> Gate | None:
        function = view

        while function is not None:
            closure = {}

            if inspect.isfunction(function):
                closure = inspect.getclosurevars(function).nonlocals

            # Every Django auth decorator wraps the view with user_passes_test,
            # whose wrapper closes over the check it runs as `test_func`. The
            # check's qualname says which decorator created it.
            if 'test_func' in closure and '_redirect_to_login' in closure:
                test_function = closure['test_func']
                test_function_name = getattr(test_function, '__qualname__', '')

                if test_function_name.startswith('login_required.'):
                    return cls(
                        has_custom_check=False,
                        permissions=(),
                        statuses_rejected=frozenset(),
                    )

                if test_function_name.startswith('permission_required.'):
                    test_closure = inspect.getclosurevars(test_function).nonlocals
                    status = HTTPStatus.FOUND

                    if test_closure['raise_exception']:
                        status = HTTPStatus.FORBIDDEN

                    return cls(
                        has_custom_check=False,
                        permissions=tuple(test_closure['perms']),
                        statuses_rejected=frozenset({status}),
                    )

                return cls(
                    has_custom_check=True,
                    permissions=(),
                    statuses_rejected=frozenset()
                )

            function = getattr(function, '__wrapped__', None)

        return None

    @classmethod
    def from_spire_view(cls, view: Callable) -> Gate | None:
        stamp = getattr(view, '__spire_gate__', None)

        if stamp is None:
            return None

        statuses_rejected = (
            frozenset({HTTPStatus.FORBIDDEN})
            if stamp.permissions else frozenset()
        )

        return cls(
            has_custom_check=stamp.has_custom_check,
            permissions=tuple(stamp.permissions),
            statuses_rejected=statuses_rejected,
        )


@dataclass(frozen=True)
class Route:
    name: str
    url: str
    method: str
    content_type: str
    requires_login: bool
    permissions: tuple[str, ...]
    has_custom_check: bool
    statuses_rejected: frozenset[int]

    @classmethod
    def from_view(cls, name: str, url: str, view: Callable) -> Route:
        gates = [
            gate
            for gate in (Gate.from_spire_view(view), Gate.from_django_view(view))
            if gate is not None
        ]

        request = getattr(view, '__spire_request__', None)

        return cls(
            name=name,
            url=url,
            method='GET' if request is None else request.method,
            content_type='' if request is None else request.content_type,
            requires_login=gates != [],
            permissions=tuple(label for gate in gates for label in gate.permissions),
            has_custom_check=any(gate.has_custom_check for gate in gates),
            statuses_rejected=frozenset().union(*(gate.statuses_rejected for gate in gates)),
        )


class Clients:
    @staticmethod
    def anonymous() -> Client:
        return Client(raise_request_exception=False)

    @staticmethod
    def superuser() -> Client:
        client = Client(raise_request_exception=False)
        client.force_login(create_super_user())

        return client

    @staticmethod
    def with_permissions(username: str, permission_labels: tuple[str, ...]) -> Client:
        user = create_user(username)

        for label in permission_labels:
            app_label, _, codename = label.partition('.')

            permission = Permission.objects.filter(
                codename=codename,
                content_type__app_label=app_label,
            ).first()

            if permission is None:
                pytest.fail(f'{label} is not a permission in the database')

            user.user_permissions.add(permission)

        client = Client(raise_request_exception=False)
        client.force_login(user)

        return client


class RouteCollector:
    def __init__(self, namespaces: Iterable[str] | None) -> None:
        self.namespaces = None if namespaces is None else frozenset(namespaces)

    def collect(self) -> tuple[list[Route], list[str]]:
        routes: list[Route] = []
        patterns_unnamed: list[str] = []

        stack = [(entry, '', {}) for entry in get_resolver().url_patterns]
        entry_count = 0

        while stack:
            entry_count += 1

            if entry_count > ROUTE_COUNT_MAX:
                message = f'url conf walk exceeded {ROUTE_COUNT_MAX} entries'
                raise RuntimeError(message)

            entry, namespace, url_kwargs = stack.pop()
            url_kwargs = {**url_kwargs, **self._pattern_url_kwargs(entry.pattern)}

            if isinstance(entry, URLResolver):
                if entry.namespace:
                    namespace = f'{namespace}{entry.namespace}:'

                stack.extend((child, namespace, url_kwargs) for child in entry.url_patterns)

                continue

            if not isinstance(entry, URLPattern):
                continue

            if not self._namespace_included(namespace):
                continue

            if not entry.name:
                patterns_unnamed.append(f'{namespace}{entry.pattern}')

                continue

            name = f'{namespace}{entry.name}'
            url = reverse(name, kwargs=url_kwargs)

            route = Route.from_view(name, url, entry.callback)
            routes.append(route)

        routes.sort(key=lambda route: route.name)
        patterns_unnamed.sort()

        return routes, patterns_unnamed

    def _namespace_included(self, namespace: str) -> bool:
        root = namespace.partition(':')[0]

        if self.namespaces is None:
            return root not in NAMESPACES_SKIPPED

        return root in self.namespaces

    @staticmethod
    def _pattern_url_kwargs(pattern: RegexPattern | RoutePattern) -> dict[str, str]:
        url_kwargs = dict.fromkeys(pattern.regex.groupindex, URL_VALUE)

        for name, converter in pattern.converters.items():
            if isinstance(converter, UUIDConverter):
                url_kwargs[name] = URL_VALUE_UUID

        return url_kwargs


class RouteRequest:
    def __init__(self, client: Client, route: Route, user: str) -> None:
        self.client = client
        self.route = route
        self.user = user
        self.response = self._fire()

    def describe(self) -> str:
        request = self.response.wsgi_request
        gate = ', '.join(self.route.permissions) if self.route.permissions else 'login only'

        description = (
            f'{self.route.name} ({request.method} {request.get_full_path()}) as {self.user} '
            f'answered {self.response.status_code}; gate: {gate}'
        )

        if self.response.exc_info is None:
            return description

        exception_type, exception, exception_traceback = self.response.exc_info
        frame = self._frame_describe(exception_traceback)

        return f'{description}; view raised {exception_type.__name__}: {exception} at {frame}'

    def verify_allowed(self, login_urls: frozenset[str]) -> None:
        description = self.describe()

        if self.response.exc_info is not None:
            raise AssertionError(description) from self.response.exc_info[1]

        assert self.response.status_code != HTTPStatus.FORBIDDEN, description
        assert self.response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR, description

        if self.response.status_code == HTTPStatus.FOUND:
            redirect_url = self.response.url.partition('?')[0]
            assert redirect_url not in login_urls, f'{description}; sent to the login page'

    def verify_rejected(self, statuses_expected: set[int]) -> None:
        description = self.describe()
        expected = ', '.join(str(status) for status in sorted(statuses_expected))

        if self.response.exc_info is not None:
            raise AssertionError(description) from self.response.exc_info[1]

        assert self.response.status_code in statuses_expected, (
            f'{description}; expected one of {expected}'
        )

    def _fire(self) -> HttpResponse:
        body = '{}' if self.route.content_type == 'application/json' else ''

        response = self.client.generic(
            self.route.method,
            self.route.url,
            data=body,
            content_type=self.route.content_type,
        )

        # A view that only accepts other methods answers 405 and names them in
        # its Allow header, so the request is refired with the first one.
        if response.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
            header = response.headers.get('Allow', 'POST')
            allowed = [method.strip() for method in header.split(',')]
            methods = [method for method in allowed if method not in ('HEAD', 'OPTIONS')]
            method = methods[0] if methods else 'POST'

            response = self.client.generic(method, self.route.url)

        return response

    @staticmethod
    def _frame_describe(exception_traceback: TracebackType) -> str:
        frames = traceback.extract_tb(exception_traceback)

        frames_project = [
            frame
            for frame in frames
            if not frame.filename.startswith(PATH_PREFIXES_THIRD_PARTY)
            and 'site-packages' not in frame.filename
        ]

        frame = frames_project[-1] if frames_project else frames[-1]
        return f'{frame.filename}:{frame.lineno} in {frame.name}'


@pytest.mark.django_db
class PermissionTests:
    namespaces: Iterable[str] | None = None
    object_routes: Iterable[str] = frozenset()
    public_routes: Iterable[str] = frozenset()

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        cls.routes, cls.patterns_unnamed = RouteCollector(cls.namespaces).collect()
        cls.routes_object = frozenset(cls.object_routes)
        cls.routes_public = frozenset(cls.public_routes)

        cls.routes_protected = [route for route in cls.routes if route.requires_login]

        cls.routes_checkable = [
            route
            for route in cls.routes_protected
            if not route.has_custom_check
        ]

        cls.routes_with_permissions = [
            route
            for route in cls.routes_checkable
            if route.permissions
        ]

        cls.login_urls = frozenset({
            resolve_url(settings.LOGIN_URL),
            reverse('django_spire:auth:admin:login'),
        })

        cls._parametrize('test_anonymous_user_is_rejected', cls.routes_protected)
        cls._parametrize('test_superuser_is_allowed', cls.routes_checkable)
        cls._parametrize('test_user_with_permission_is_allowed', cls.routes_with_permissions)
        cls._parametrize('test_user_without_permission_is_rejected', cls.routes_with_permissions)

    @classmethod
    def _parametrize(cls, name: str, routes: list[Route]) -> None:
        method = getattr(cls, name)

        # Each subclass gets its own copy of the method, so the parametrize
        # mark holds that subclass's routes and never leaks to a sibling.
        def method_copy(self: PermissionTests, route: Route) -> None:
            method(self, route)

        method_copy.__name__ = name
        method_copy.__qualname__ = f'{cls.__qualname__}.{name}'

        ids = [route.name for route in routes]
        setattr(cls, name, pytest.mark.parametrize('route', routes, ids=ids)(method_copy))

    def test_anonymous_user_is_rejected(self, route: Route) -> None:
        expected = {HTTPStatus.FOUND}

        if route.has_custom_check:
            expected.add(HTTPStatus.FORBIDDEN)

        if route.name in self.routes_object:
            expected.add(HTTPStatus.FORBIDDEN)
            expected.add(HTTPStatus.NOT_FOUND)

        RouteRequest(Clients.anonymous(), route, 'anonymous').verify_rejected(expected)

    def test_declared_permissions_exist(self) -> None:
        declared = {label for route in self.routes_protected for label in route.permissions}

        known_rows = Permission.objects.values_list('content_type__app_label', 'codename')
        known = {f'{app_label}.{codename}' for app_label, codename in known_rows}

        unknown = sorted(declared - known)

        assert unknown == [], f'views require permissions that do not exist: {unknown}'

    def test_every_route_has_a_name(self) -> None:
        unnamed = self.patterns_unnamed

        assert unnamed == [], f'unnamed routes cannot be tested: {unnamed}'

    def test_every_route_is_protected_or_public(self) -> None:
        assert self.routes != [], 'no routes found; check the namespaces'

        unprotected = {route.name for route in self.routes if not route.requires_login}

        missing = sorted(unprotected - self.routes_public)
        stale = sorted(self.routes_public - unprotected)

        assert missing == [], f'routes without a permission decorator: {missing}'
        assert stale == [], f'public_routes entries that are now protected or gone: {stale}'

    def test_object_routes_are_protected(self) -> None:
        stale = sorted(self.routes_object - {route.name for route in self.routes_protected})

        assert stale == [], f'object_routes entries that are not protected routes: {stale}'

    def test_superuser_is_allowed(self, route: Route) -> None:
        RouteRequest(Clients.superuser(), route, 'superuser').verify_allowed(self.login_urls)

    def test_user_with_permission_is_allowed(self, route: Route) -> None:
        client = Clients.with_permissions('with_permission', route.permissions)
        RouteRequest(client, route, 'user with permission').verify_allowed(self.login_urls)

    def test_user_without_permission_is_rejected(self, route: Route) -> None:
        client = Clients.with_permissions('without_permission', ())
        expected = set(route.statuses_rejected)

        if route.name in self.routes_object:
            expected.add(HTTPStatus.NOT_FOUND)

        RouteRequest(client, route, 'user without permission').verify_rejected(expected)
