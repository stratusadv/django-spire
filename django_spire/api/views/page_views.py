from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('api').permission_required('can_view')
def access_list_view(request: WSGIRequest) -> TemplateResponse:
    context_data = {'api_accesses': ApiAccess.objects.active()}

    context_data['page_title'] = 'Api Access'
    context_data['page_description'] = 'List View'
    context_data['breadcrumbs'] = [{'name': 'API Access', 'href': None}]

    return TemplateResponse(
        request, context=context_data, template='django_spire/api/page/access_list_page.html'
    )


@AppAuthController('api').permission_required('can_delete')
def access_delete_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect | TemplateResponse:
    api_access = get_object_or_404(ApiAccess, pk=pk)
    return_url = request.GET.get('return_url', reverse('django_spire:api:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=api_access)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                api_access.set_deleted()
                api_access.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=(
                        f'{request.user.get_full_name()} deleted API access "{api_access}".'
                    ),
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=api_access)

    return TemplateResponse(
        request,
        context={
            'request': request,
            'form': form,
            'form_title': f'Delete {api_access}',
            'form_description': f'Are you sure you would like to delete API access "{api_access}"?',
            'django_spire_navigation': {
                'page_title': 'Delete API Access',
                'breadcrumbs': [
                    {'name': 'API Access', 'href': reverse('django_spire:api:page:list')},
                    {'name': str(api_access), 'href': None},
                    {'name': 'Delete', 'href': None},
                ],
            },
        },
        template='django_spire/page/delete_confirmation_form_page.html',
    )
