import json
from typing import Optional, Union

from django import forms

from django_spire.file import widgets
from django_spire.file.models import File
from django_spire.file.queryset import FileQuerySet


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widgets.MultipleWidget()

    def prepare_value(self, value: Optional[list[File]]):
        if value is not None:
            return json.dumps([file.to_dict() for file in value])
        else:
            return json.dumps([])

    def clean(self, data, initial=None) -> dict:
        return data


class SingleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = widgets.SingleFileWidget()

    def prepare_value(self, value: Union[File, FileQuerySet, None]) -> Optional[str]:
        if isinstance(value, FileQuerySet):
            value =  value.first()

        if value is not None:
            return value.to_json()
        else:
            return json.dumps(None)

    def clean(self, data, initial=None) -> dict:
        return data
