from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django_spire.contrib.form.utils import show_form_errors
from django_spire.core.redirect import safe_redirect_url
from django_spire.notification import models
from test_project.apps.notification.forms import NotificationForm


def notification_form_view(request, pk: int):
    notification = get_object_or_404(models.Notification, pk=pk)

    if request.method == 'POST':
        form = NotificationForm(request.POST, instance=notification)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse(
                'notification:page:list',
            ))

        show_form_errors(request, form)
    return HttpResponseRedirect(safe_redirect_url(request))
