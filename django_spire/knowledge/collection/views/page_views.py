from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.knowledge.collection.models import Collection

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_view')
def top_level_collection_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    collection = get_object_or_404(Collection, pk=pk)

    context = {
        'collection': collection,
        'collection_tree_json': Collection.services.transformation.to_hierarchy_json(
            request=request, parent_id=collection.id
        ),
    }
    context['page_title'] = 'Knowledge Collection'
    context['page_description'] = ''
    context['breadcrumbs'] = [
        {'name': 'Knowledge', 'href': reverse('django_spire:knowledge:page:home')},
        {'name': str(collection), 'href': None},
    ]
    return TemplateResponse(
        request, 'django_spire/knowledge/collection/page/display_page.html', context=context
    )


@AppAuthController('knowledge').permission_required('can_delete')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    collection = get_object_or_404(Collection, pk=pk)

    if collection.parent:
        return_url = request.GET.get(
            'return_url',
            reverse(
                'django_spire:knowledge:collection:page:top_level',
                kwargs={'pk': collection.parent_id},
            ),
        )
    else:
        return_url = request.GET.get('return_url', reverse('django_spire:knowledge:page:home'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=collection)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                collection.services.processor.set_deleted()
                collection.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=(
                        f'{request.user.get_full_name()} deleted collection "{collection}".'
                    ),
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=collection)

    return TemplateResponse(
        request,
        context={
            'form': form,
            'form_title': f'Delete {collection}',
            'form_description': (
                f'Are you sure you would like to delete collection "{collection}"?'
            ),
            'django_spire_navigation': {
                'page_title': 'Delete Collection',
                'breadcrumbs': [
                    {'name': 'Knowledge', 'href': reverse('django_spire:knowledge:page:home')},
                    {'name': str(collection), 'href': None},
                    {'name': 'Delete', 'href': None},
                ],
            },
        },
        template='django_spire/page/delete_confirmation_form_page.html',
    )
