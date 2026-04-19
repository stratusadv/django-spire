from __future__ import annotations

from django import forms

from django_spire.file.fields import MultipleFileField, SingleFileField
from django_spire.file.handlers import SingleFileHandler


class FileForm(forms.Form):
    files = MultipleFileField()


class FileFormMixin:
    def save(self, commit: bool = True):
        instance = super().save(commit=commit)

        if commit:
            self._save_file_fields(instance)

        return instance

    def _save_file_fields(self, instance) -> None:
        for name, field in self.fields.items():
            if isinstance(field, SingleFileField):
                handler = SingleFileHandler(related_field=field.related_field)
                handler.save(self.cleaned_data.get(name), instance)


class FileModelForm(FileFormMixin, forms.ModelForm):
    ...
