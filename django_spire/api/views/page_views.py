from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.api.navigation import ApiNavigation
from django_spire.auth.permissions.decorators import permission_required
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_api.view_apiaccess')
def access_list_view(request: WSGIRequest) -> TemplateResponse:
    nav = ApiNavigation()
    nav.page_title = 'Api Access'
    nav.page_description = 'List View'
    nav.breadcrumbs.add('API Access')
    context = nav.as_context()
    context['api_accesses'] = ApiAccess.objects.active().select_related('user')
    return TemplateResponse(request, 'django_spire/api/page/access_list_page.html', context=context)


@permission_required('django_spire_api.delete_apiaccess')
def access_delete_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect | TemplateResponse:
    api_access = get_object_or_404(ApiAccess, pk=pk)
    return_url = request.GET.get('return_url', reverse('django_spire:api:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=api_access)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                api_access.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=api_access)

    nav = ApiNavigation()
    nav.page_title = 'Delete API Access'
    nav.breadcrumbs.add('API Access', 'django_spire:api:page:list')
    nav.breadcrumbs.add(str(api_access))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {api_access}'
    context['form_description'] = (
        f'Are you sure you would like to delete API access "{api_access}"?'
    )
    return TemplateResponse(
        request,
        'django_spire/page/delete_confirmation_form_page.html',
        context=context,
    )
