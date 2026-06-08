from __future__ import annotations

from django_glue import Glue

from typing import TYPE_CHECKING

from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_spire.auth.controller.controller import AppAuthController
from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.file.factory import FileFactory
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.forms import EntryForm, EntryFilesForm
from django_spire.knowledge.entry.version.maps import FILE_TYPE_CONVERTER_MAP

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@AppAuthController('knowledge').permission_required('can_add')
def form_view(
    request: WSGIRequest, collection_pk: int, pk: int = 0
) -> TemplateResponse | HttpResponseRedirect:
    entry = get_object_or_null_obj(Entry, pk=pk)
    collection = Collection.objects.get(pk=collection_pk)

    Glue.model(request, 'entry', entry, fields=['name'])

    if request.method == 'POST':
        form = EntryForm(request.POST, instance=entry)

        if form.is_valid():
            form.cleaned_data['collection'] = collection
            entry, _ = entry.services.save_model_obj(author=request.user, **form.cleaned_data)

            return HttpResponseRedirect(
                reverse('django_spire:knowledge:entry:version:page:editor', kwargs={'pk': entry.pk})
            )

        show_form_errors(request, form)
    else:
        form = EntryForm(instance=entry)

    return TemplateResponse(
        request,
        context={
            'request': request,
            'form': form,
            'entry': entry,
            'page_title': 'Entry',
            'page_description': 'Edit' if pk else 'Create',
            'breadcrumbs': [
                {
                    'name': 'Entries',
                    'href': reverse(
                        'django_spire:knowledge:entry:page:list',
                        kwargs={'collection_pk': collection_pk},
                    ),
                },
                {
                    'name': collection.name,
                    'href': reverse(
                        'django_spire:knowledge:collection:page:detail',
                        kwargs={'pk': collection_pk},
                    ),
                },
                {'name': 'Edit' if pk else 'Create', 'href': None},
            ],
            'action_url': (
                reverse(
                    'django_spire:knowledge:entry:form:create',
                    kwargs={'collection_pk': collection_pk},
                )
                if not entry.pk
                else reverse(
                    'django_spire:knowledge:entry:form:update',
                    kwargs={'collection_pk': collection_pk, 'pk': entry.pk},
                )
            ),
        },
        template='django_spire/knowledge/entry/page/form_page.html',
    )


@AppAuthController('knowledge').permission_required('can_add')
def import_form_view(
    request: WSGIRequest, collection_pk: int
) -> TemplateResponse | HttpResponseRedirect:
    Glue.queryset(request, 'collections', Collection.objects.active(), fields=['name'])

    if request.method == 'POST':
        file_form = EntryFilesForm(request.POST, request.FILES)

        if file_form.is_valid():
            factory = FileFactory(app_name='knowledge')

            file_objects = factory.create_many(request.FILES.getlist('import_files'))

            Entry.services.factory.create_from_files(
                author=request.user,
                collection=Collection.objects.get(pk=collection_pk),
                files=file_objects,
            )

            return HttpResponseRedirect(
                reverse(
                    'django_spire:knowledge:entry:template:file_list',
                    kwargs={'collection_pk': collection_pk},
                )
            )

        show_form_errors(request, file_form)

    supported_file_types = ['.' + file_type for file_type in list(FILE_TYPE_CONVERTER_MAP.keys())]
    breadcrumbs = [{'name': 'Import Files', 'href': None}]

    context = {
        'collection_pk': collection_pk,
        'supported_file_types': supported_file_types,
        'supported_file_types_verbose': ', '.join(supported_file_types),
    }
    context['page_title'] = 'Import Files'
    context['page_description'] = 'Import Files'
    context['breadcrumbs'] = breadcrumbs
    return TemplateResponse(
        request, 'django_spire/knowledge/entry/page/import_form_page.html', context=context
    )
