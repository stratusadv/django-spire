from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from django.core.handlers.wsgi import WSGIRequest

from django_spire.core.redirect import safe_redirect_url

from django_spire.notification.app.models import AppNotification


def delete_notification_json_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect:
    notification = get_object_or_404(AppNotification, pk=pk)
    notification.set_deleted()

    return HttpResponseRedirect(safe_redirect_url(request))
