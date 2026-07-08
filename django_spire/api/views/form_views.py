from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from django.template.response import TemplateResponse
from django.urls import reverse

from django_glue import Glue

from django_spire.api import forms
from django_spire.api.models import ApiAccess
from django_spire.api.navigation import ApiNavigation
from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.shortcuts import get_object_or_null_obj

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


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

            nav = ApiNavigation()
            nav.page_title = 'API Access Created'
            nav.page_description = 'Your API access has been created.'
            nav.breadcrumbs.add('API Access', 'django_spire:api:page:list')
            nav.breadcrumbs.add('Created')
            context = nav.as_context()
            context['api_access'] = api_access
            context['raw_key'] = raw_key
            return TemplateResponse(
                request, 'django_spire/api/page/access_created_page.html', context=context
            )

        show_form_errors(request, form)

    else:
        form = forms.ApiAccessCreateForm(instance=api_access)

    nav = ApiNavigation()
    nav.page_title = api_access._meta.verbose_name.title()
    nav.page_description = 'Create'
    nav.breadcrumbs.add('API Access', 'django_spire:api:page:list')
    nav.breadcrumbs.add('Create')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Create {api_access._meta.verbose_name.title()}'
    context['form_description'] = ''
    context['form_action_url'] = reverse('django_spire:api:form:create')
    return TemplateResponse(request, 'django_spire/api/page/access_form_page.html', context=context)
