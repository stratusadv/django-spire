from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.file.factory import FileFactory
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.entry.models import Entry

if TYPE_CHECKING:
    from django.http import HttpRequest


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['name']


class EntryFilesForm(forms.Form):
    import_files = forms.FileField()
    collection_pk = forms.IntegerField()

    @Glue.attribute(access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        files = self.files.getlist('import_files.value')

        if not files:
            return GlueResponse(messages=[GlueMessage.error('No files selected.')])

        collection_pk = int(self.data.get('collection_pk') or 0)
        collection = get_object_or_null_obj(Collection, pk=collection_pk)

        file_objects = FileFactory(app_name='knowledge').create_many(files)

        Entry.services.factory.create_from_files(
            author=request.user,
            collection=collection,
            files=file_objects
        )

        return GlueResponse(
            result={
                'redirect': {
                    'url': reverse(
                        'django_spire:knowledge:entry:template:file_list',
                        kwargs={'collection_pk': collection_pk},
                    )
                }
            }
        )
