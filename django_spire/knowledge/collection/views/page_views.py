from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.navigation import CollectionNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_view')
def top_level_collection_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    collection = get_object_or_404(Collection, pk=pk)

    nav = CollectionNavigation()
    nav.page_title = 'Knowledge Collection'
    nav.page_description = ''
    nav.breadcrumbs.add('Collections', 'django_spire:knowledge:page:home')
    nav.breadcrumbs.add(str(collection))
    context = nav.as_context()
    context['collection'] = collection
    context['collection_tree_json'] = Collection.services.transformation.to_hierarchy_json(
        request=request, parent_id=collection.id
    )
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

    nav = CollectionNavigation()
    nav.page_title = 'Delete Collection'
    nav.breadcrumbs.add('Knowledge', 'django_spire:knowledge:page:home')
    nav.breadcrumbs.add(str(collection))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {collection}'
    context['form_description'] = (
        f'Are you sure you would like to delete collection "{collection}"?'
    )
    return TemplateResponse(
        request,
        context=context,
        template='django_spire/contrib/page/delete_confirmation_form_page.html',
    )
