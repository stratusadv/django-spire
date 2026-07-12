from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.navigation import EntryNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_delete')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    entry = get_object_or_404(Entry, pk=pk)
    return_url = request.GET.get('return_url', reverse('django_spire:knowledge:page:home'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=entry)

        if form.is_valid():
            entry.set_deleted()
            entry.add_activity(
                user=request.user,
                verb='deleted',
                information=f'{request.user.get_full_name()} deleted entry "{entry}".',
            )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=entry)

    nav = EntryNavigation()
    nav.page_title = 'Delete Entry'

    temp_collection = entry.collection

    breadcrumbs = []

    while temp_collection:
        breadcrumbs.append(
            {
                'name': str(temp_collection),
                'view_name': 'django_spire:knowledge:collection:page:top_level',
                'view_kwargs': {'pk': temp_collection.pk},
            }
        )
        temp_collection = temp_collection.parent

    for crumb in reversed(breadcrumbs):
        nav.breadcrumbs.add(**crumb)

    nav.breadcrumbs.add(str(entry))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {entry}'
    context['form_description'] = f'Are you sure you would like to delete entry "{entry}"?'
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/knowledge/collection/form/delete_confirmation_form_page.html',
    )



