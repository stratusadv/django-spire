from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.collection.models import Collection

if TYPE_CHECKING:
    from django.template.response import TemplateResponse
    from django.core.handlers.wsgi import WSGIRequest

    from django_spire.contrib.breadcrumb import Breadcrumbs


@AppAuthController('knowledge').permission_required('can_view')
def home_view(request: WSGIRequest) -> TemplateResponse:
    def breadcrumbs_func(breadcrumbs: Breadcrumbs):
        breadcrumbs.add_breadcrumb(name='Knowledge')

    return portal_views.list_view(
        request,
        model=Collection,
        breadcrumbs_func=breadcrumbs_func,
        context_data={
            'collections': Collection.objects.active().parentless().request_user_has_access(request),
        },
        template='django_spire/knowledge/page/home_page.html',
    )
