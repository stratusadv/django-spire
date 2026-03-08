from __future__ import annotations

from typing import ClassVar

from django import forms

from django_spire.api.models import ApiAccess


class ApiAccessCreateForm(forms.ModelForm):
    class Meta:
        model = ApiAccess
        exclude: ClassVar[list] = ['hashed_key', 'key_hint']


