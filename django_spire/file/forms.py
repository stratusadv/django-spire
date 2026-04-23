from __future__ import annotations

from django import forms

from django_spire.file.fields import MultipleFileField


class FileForm(forms.Form):
    files = MultipleFileField()
