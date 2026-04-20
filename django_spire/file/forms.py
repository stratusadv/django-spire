from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from django_spire.file.fields import MultipleFileField, SingleFileField
from django_spire.file.handlers import MultiFileHandler, SingleFileHandler

if TYPE_CHECKING:
    from django.db import models


class FileForm(forms.Form):
    files = MultipleFileField()


class FileFormMixin:
    def save(self, commit: bool = True) -> models.Model:
        instance = super().save(commit=commit)

        if commit:
            self._save_file_fields(instance)

        return instance

    def _save_file_fields(self, instance: models.Model) -> None:
        for name, field in self.fields.items():
            data = self.cleaned_data.get(name)

            if isinstance(field, SingleFileField):
                handler = SingleFileHandler.for_related_field(
                    field.related_field,
                    validator=field.validator,
                )

                handler.replace(data, instance)

            if isinstance(field, MultipleFileField):
                handler = MultiFileHandler.for_related_field(
                    field.related_field,
                    validator=field.validator,
                )

                handler.replace(data, instance)


class FileModelForm(FileFormMixin, forms.ModelForm):
    ...
