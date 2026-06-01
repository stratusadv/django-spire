from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from django.urls import reverse

from django_glue import Glue

from django_spire.api import forms
from django_spire.api.models import ApiAccess
from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.breadcrumb.breadcrumbs import Breadcrumbs
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.shortcuts import get_object_or_null_obj

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.template.response import TemplateResponse


@AppAuthController('api').permission_required('can_add')
def access_create_form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    api_access = get_object_or_null_obj(ApiAccess, pk=pk)

    Glue.model(request, unique_name='api_access', target=api_access)

    if request.method == 'POST':
        form = forms.ApiAccessCreateForm(request.POST)

        if form.is_valid():
            api_access: ApiAccess = form.save()

            raw_key = uuid4().hex

            api_access.set_key_and_save(raw_key)

            return generic_views.template_view(
                request,
                page_title='API Access Created',
                page_description='Your API access has been created.',
                breadcrumbs=Breadcrumbs(),
                template='django_spire/api/page/access_created_page.html',
                context_data={
                    'api_access': api_access,
                    'raw_key': raw_key,
                }
            )

        show_form_errors(request, form)

    else:
        form = forms.ApiAccessCreateForm(instance=api_access)

    return generic_views.form_view(
        request,
        form=form,
        verb='Create',
        obj=api_access,
        template='django_spire/api/page/access_form_page.html',
        context_data={
            'form_action_url': reverse('django_spire:api:form:create'),
        }
    )
