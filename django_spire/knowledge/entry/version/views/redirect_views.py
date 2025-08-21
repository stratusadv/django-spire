from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.knowledge.entry.version.models import EntryVersion


@login_required
def publish_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect:
    version = get_object_or_404(EntryVersion, pk=pk)
    version.services.processor.publish()

    return HttpResponseRedirect(
        reverse(
            'django_spire:knowledge:entry:version:page:detail',
            kwargs={'pk': version.pk}
        )
    )
