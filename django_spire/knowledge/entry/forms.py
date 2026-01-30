from __future__ import annotations

from django import forms

from django_spire.knowledge.entry.models import Entry


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['name']


class EntryFilesForm(forms.Form):
    collection = forms.IntegerField(required=True)
    import_files = forms.FileField()
