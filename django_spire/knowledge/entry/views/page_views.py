from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.contrib.generic_views import portal_views
from django_spire.knowledge.entry.models import Entry


@login_required()
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    entry = get_object_or_404(Entry, pk=pk)

    return portal_views.delete_form_view(
        request,
        obj=entry,
        return_url=request.GET.get(
            'return_url',
            reverse(
                'django_spire:knowledge:collection:page:detail',
                kwargs={'pk': entry.collection.pk}
            )
        )
    )
