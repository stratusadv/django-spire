from __future__ import annotations

from typing import TYPE_CHECKING

from django.template.response import TemplateResponse
from django.urls import reverse

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def demo_page_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'tab_overview_endpoint': reverse('lazy_tabs:template:tab_overview'),
        'tab_details_endpoint': reverse('lazy_tabs:template:tab_details'),
        'tab_settings_endpoint': reverse('lazy_tabs:template:tab_settings'),
        'tab_profile_endpoint': reverse('lazy_tabs:template:tab_profile'),
        'tab_activity_endpoint': reverse('lazy_tabs:template:tab_activity'),
        'tab_items_endpoint': reverse('lazy_tabs:template:tab_items'),
        'tab_table_endpoint': reverse('lazy_tabs:template:tab_table'),
    }

    return TemplateResponse(
        request=request,
        context=context_data,
        template='lazy_tabs/page/demo_page.html',
    )
