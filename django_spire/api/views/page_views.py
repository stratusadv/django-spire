from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.template.response import TemplateResponse

from django_spire.api.models import ApiAccess
from django_spire.api.navigation import ApiNavigation
from django_spire.auth.permissions.decorators import permission_required
from django_spire.history.activity.models import Activity

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_api.view_apiaccess')
def access_list_view(request: WSGIRequest) -> TemplateResponse:
    nav = ApiNavigation()

    context = nav.as_context()
    context['api_accesses'] = ApiAccess.objects.active().select_related('user')
    context['activity_log'] = Activity.objects.prefetch_user().filter(
        content_type=ContentType.objects.get_for_model(ApiAccess)
    ).order_by('-created_datetime')[:20]

    return TemplateResponse(request, 'django_spire/api/page/access_list_page.html', context=context)
