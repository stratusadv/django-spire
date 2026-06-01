from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue
from django_spire.contrib.generic_views import page_views
from django_spire.notification import models
from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
    NotificationPriorityChoices,
)
from test_project.app.notification.forms import NotificationForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def notification_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    notification = get_object_or_404(models.Notification, pk=pk)

    context_data = {
        'notification': notification,
    }

    return generic_views.detail_view(
        request,
        obj=notification,
        context_data=context_data,
        template='notification/page/notification_detail_page.html'
    )


@login_required()
def notification_form_view(request, pk: int):
    if pk == 0:
        notification = models.Notification.objects.create(user=request.user)

        return HttpResponseRedirect(
            reverse('notification:page:form', kwargs={'pk': notification.pk})
        )
    else:
        notification = models.Notification.objects.get(pk=pk)

    Glue.model(
        request=request,
        target=notification,
        unique_name='notification',
    )

    return generic_views.form_view(
        request,
        obj=notification,
        context_data={
            "notification": notification
        },
        template="notification/form/page/form_page.html",
        form=NotificationForm(instance=notification)
    )


@login_required()
def notification_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'notification/page/notification_home_page.html'
    return TemplateResponse(request, template)


@login_required()
def notification_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'notifications': (
            models.Notification.objects
            .all()
            .order_by('-created_datetime')
            .prefetch_related('sms', 'email')
        ),
        'statuses': NotificationStatusChoices,
        'types': NotificationTypeChoices,
        'priorities': NotificationPriorityChoices
    }

    return generic_views.list_view(
        request,
        model=models.Notification,
        context_data=context_data,
        template='notification/page/notification_list_page.html'
    )
