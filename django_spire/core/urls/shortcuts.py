from typing import Callable

from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponse
from django.urls import path
from django.urls.conf import include

from django_spire.auth.group.decorators import permission_required
from django_spire.core.urls.permissions import ViewPermissionController


def _view_with_permissions(
        view_callable: Callable[[WSGIRequest, ...], HttpResponse],
        permissions_decorator: Callable[[tuple[str, ...], bool], callable] = permission_required,
        permissions: str | tuple[str, ...] = None,
):
    if permissions is None:
        return view_callable

    if isinstance(permissions, str):
        permissions = (permissions,)

    return permissions_decorator(permissions, True)(view_callable)

def _include_namespace_urls_with_permissions(
    url_patterns: list[tuple[str, Callable[[WSGIRequest, ...], HttpResponse], str]],
    permission_controller: type[ViewPermissionController],
):
    return [
        path(
            route=route,
            view=_view_with_permissions(
                permissions=permission_controller.url_permissions_map.get(name, None),
                view_callable=view,
                permissions_decorator=permission_controller.permissions_required_decorator
            ),
            name=name
        )
        for route, view, name in url_patterns
    ]


def include_app_urls_with_permissions(
        app_name: str,
        namespace_url_patterns: list[tuple[str, list[tuple[str, Callable[[WSGIRequest, ...], HttpResponse], str]]]],
        permission_controller: type[ViewPermissionController]
):
    return [
        path(
            f'{namespace}/',
            include(
                (_include_namespace_urls_with_permissions(url_patterns, permission_controller), app_name),
                namespace=namespace
            ),
            kwargs={'permission_controller': permission_controller}
        )
        for namespace, url_patterns in namespace_url_patterns
    ]
