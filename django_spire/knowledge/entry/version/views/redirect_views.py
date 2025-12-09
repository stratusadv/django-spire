from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.knowledge.entry.version.models import EntryVersion

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_change')
def publish_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect:
    version = get_object_or_404(EntryVersion, pk=pk)
    version.services.processor.publish()

    return HttpResponseRedirect(
        reverse(
            'django_spire:knowledge:entry:version:page:editor',
            kwargs={'pk': version.pk}
        )
    )
