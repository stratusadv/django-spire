from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.permissions.decorators import permission_required
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.knowledge.collection.breadcrumbs import add_collection_chain_breadcrumbs
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.navigation import EntryNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_knowledge.delete_collection')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    entry = get_object_or_404(Entry, pk=pk)
    return_url = request.GET.get('return_url', reverse('django_spire:knowledge:page:home'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=entry)

        if form.is_valid():
            entry.set_deleted()

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=entry)

    nav = EntryNavigation()
    nav.page_title = 'Delete Entry'

    add_collection_chain_breadcrumbs(nav.breadcrumbs, entry.collection)

    nav.breadcrumbs.add(str(entry))
    nav.breadcrumbs.add('Delete')

    return TemplateResponse(
        request,
        context=nav.as_context() | {
            'form': form,
            'form_title': f'Delete {entry}',
            'form_description': f'Are you sure you would like to delete entry "{entry}"?',
        },
        template='django_spire/knowledge/collection/form/delete_confirmation_form_page.html',
    )



