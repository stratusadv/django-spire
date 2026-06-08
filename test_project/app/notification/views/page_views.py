from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from test_project.app.notification.forms import NotificationForm

from django_spire.notification import models
from django_spire.notification.choices import (
    NotificationStatusChoices,
    NotificationTypeChoices,
    NotificationPriorityChoices,
)

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@login_required()
def notification_detail_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    notification = get_object_or_404(models.Notification, pk=pk)

    context_data = {'notification': notification}

    context_data['page_title'] = str(notification)
    context_data['page_description'] = 'Detail View'
    context_data['breadcrumbs'] = [
        {'name': 'Notifications', 'href': None},
        {'name': str(notification), 'href': None},
    ]

    return TemplateResponse(
        request, context=context_data, template='notification/page/notification_detail_page.html'
    )


@login_required()
def notification_form_view(
    request: WSGIRequest, pk: int
) -> TemplateResponse | HttpResponseRedirect:
    if pk == 0:
        notification = models.Notification.objects.create(user=request.user)

        return HttpResponseRedirect(
            reverse('notification:page:form', kwargs={'pk': notification.pk})
        )

    notification = models.Notification.objects.get(pk=pk)

    Glue.model(request=request, target=notification, unique_name='notification')

    context_data = {
        'request': request,
        'notification': notification,
        'obj': notification,
        'form': NotificationForm(instance=notification),
    }
    context_data['page_title'] = 'Notification'
    context_data['page_description'] = 'Edit'
    context_data['breadcrumbs'] = [
        {'name': 'Notifications', 'href': None},
        {'name': str(notification), 'href': None},
    ]

    return TemplateResponse(
        request, context=context_data, template='notification/form/page/form_page.html'
    )


@login_required()
def notification_home_view(request: WSGIRequest) -> TemplateResponse:
    template = 'notification/page/notification_home_page.html'
    return TemplateResponse(request, template)


@login_required()
def notification_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {
        'notifications': (
            models.Notification.objects.all()
            .order_by('-created_datetime')
            .prefetch_related('sms', 'email')
        ),
        'statuses': NotificationStatusChoices,
        'types': NotificationTypeChoices,
        'priorities': NotificationPriorityChoices,
    }

    context_data['page_title'] = 'Notification'
    context_data['page_description'] = 'List View'
    context_data['breadcrumbs'] = [{'name': 'Notifications', 'href': None}]

    return TemplateResponse(
        request, context=context_data, template='notification/page/notification_list_page.html'
    )
