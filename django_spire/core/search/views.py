from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

from django_spire.core.search.registry import get_search_registry

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

    from django_spire.core.search.command import SearchCommand
    from django_spire.core.search.search import Search


def _user_search_instances(request: WSGIRequest) -> list[Search]:
    search_instances: list[Search] = []

    for search_class in get_search_registry().values():
        search = search_class()

        if search.permission_required and not request.user.has_perm(search.permission_required):
            continue

        search_instances.append(search)

    return search_instances


def _user_commands(search: Search, request: WSGIRequest, query_string: str) -> list[SearchCommand]:
    return [
        command
        for command in search.commands_for_query(query_string)
        if not command.permission_required or request.user.has_perm(command.permission_required)
    ]


def _sections(search_instances: list[Search]) -> list[dict]:
    return [
        {'name': search.section_name, 'icon': search.icon}
        for search in search_instances
    ]


def _run_searches(
    search_instances: list[Search], request: WSGIRequest, query_string: str
) -> list[dict]:
    results_by_section: list[dict] = []

    for search in search_instances:
        results = []

        list_result = search.list_result(query_string)

        if list_result:
            results.append(list_result)

        results.extend(
            search.command_result(command)
            for command in _user_commands(search, request, query_string)
        )

        obj_list = list(search.search(request, query_string) or [])

        results.extend(search.to_result(obj) for obj in obj_list)

        if results:
            results_by_section.append(
                {
                    'name': search.section_name,
                    'icon': search.icon,
                    'results': results,
                }
            )

    return results_by_section


def _search_context(request: WSGIRequest, query_string: str) -> dict:
    search_instances = _user_search_instances(request)

    context = {'query': query_string, 'sections': _sections(search_instances)}

    if query_string:
        context['results_by_section'] = _run_searches(search_instances, request, query_string)

    return context


@login_required()
def search_palette_view(request: WSGIRequest) -> TemplateResponse:
    query_string = request.GET.get('q', '').strip()

    context = _search_context(request, query_string)

    return TemplateResponse(
        request,
        context=context,
        template='django_spire/search/modal/search_palette_modal_content.html',
    )


@login_required()
def search_results_view(request: WSGIRequest) -> TemplateResponse:
    query_string = request.GET.get('q', '').strip()

    context = _search_context(request, query_string)

    return TemplateResponse(
        request, context=context, template='django_spire/search/element/search_element.html'
    )
