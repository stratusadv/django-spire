from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.api import forms
from django_spire.api.models import ApiAccess
from django_spire.api.navigation import ApiNavigation
from django_spire.auth.permissions.decorators import permission_required
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.shortcuts import get_object_or_null_obj

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_api.add_apiaccess')
def access_create_form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    api_access = get_object_or_null_obj(ApiAccess, pk=pk)

    if request.method == 'POST':
        form = forms.ApiAccessCreateForm(request.POST, user=request.user)

        if form.is_valid():
            api_access: ApiAccess = form.save()

            raw_key = uuid4().hex

            api_access.set_key_and_save(raw_key)

            nav = ApiNavigation()
            nav.page_title = 'API Access Created'
            nav.breadcrumbs.add(api_access.name, view_name='django_spire:api:page:list')
            nav.breadcrumbs.add('Created')
            context = nav.as_context()
            context['api_access'] = api_access
            context['raw_key'] = raw_key
            return TemplateResponse(
                request, 'django_spire/api/page/access_created_page.html', context=context
            )

        show_form_errors(request, form)

    else:
        form = forms.ApiAccessCreateForm(instance=api_access, user=request.user)

    nav = ApiNavigation()
    nav.set_page_title_to_form_action_from_model_instance(api_access)
    nav.breadcrumbs.add('New API Access Key')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Create {api_access._meta.verbose_name.title()}'
    context['form_description'] = ''
    context['form_action_url'] = reverse('django_spire:api:form:create')
    return TemplateResponse(request, 'django_spire/api/page/access_form_page.html', context=context)


@permission_required('django_spire_api.delete_apiaccess')
def access_delete_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect | TemplateResponse:
    api_access = get_object_or_404(ApiAccess, pk=pk)
    return_url = request.GET.get('return_url', reverse('django_spire:api:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=api_access)

        if form.is_valid():
            api_access.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=api_access)

    nav = ApiNavigation()
    nav.page_title = 'Delete API Access'
    nav.breadcrumbs.add(str(api_access), view_name='django_spire:api:page:list')
    nav.breadcrumbs.add('Delete')

    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {api_access}'
    context['return_url'] = return_url

    return TemplateResponse(
        request,
        'django_spire/api/form/delete_confirmation_form_page.html',
        context=context,
    )
