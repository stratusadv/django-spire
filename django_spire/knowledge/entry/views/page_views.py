from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.entry.models import Entry


@AppAuthController('knowledge').permission_required('can_delete')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    entry = get_object_or_404(Entry, pk=pk)

    return portal_views.delete_form_view(
        request,
        obj=entry,
        delete_func=entry.services.processor.set_deleted,
        return_url=request.GET.get(
            'return_url',
            reverse(
                'django_spire:knowledge:collection:page:detail',
                kwargs={'pk': entry.collection.pk}
            )
        )
    )
