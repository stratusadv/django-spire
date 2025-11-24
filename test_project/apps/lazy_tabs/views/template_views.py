from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def tab_overview_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/overview.html',
    )


def tab_details_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/details.html',
    )


def tab_settings_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/settings.html',
    )


def tab_profile_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/profile.html',
    )


def tab_activity_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {}

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/tab/activity.html',
    )
