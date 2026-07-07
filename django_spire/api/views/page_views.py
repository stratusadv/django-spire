from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.api.navigation import ApiNavigation
from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('api').permission_required('can_view')
def access_list_view(request: WSGIRequest) -> TemplateResponse:
    nav = ApiNavigation()
    nav.page_title = 'Api Access'
    nav.page_description = 'List View'
    nav.breadcrumbs.add('API Access', None)
    context = nav.as_context()
    context['api_accesses'] = ApiAccess.objects.active()
    return TemplateResponse(request, 'django_spire/api/page/access_list_page.html', context=context)


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

    nav = ApiNavigation()
    nav.page_title = 'Delete API Access'
    nav.breadcrumbs.add('API Access', reverse('django_spire:api:page:list'))
    nav.breadcrumbs.add(str(api_access), None)
    nav.breadcrumbs.add('Delete', None)
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {api_access}'
    context['form_description'] = (
        f'Are you sure you would like to delete API access "{api_access}"?'
    )
    return TemplateResponse(
        request, 'django_spire/contrib/page/../../core/templates/django_spire/page/delete_confirmation_form_page.html', context=context
    )
