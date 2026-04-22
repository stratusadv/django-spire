from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from test_project.apps.lazy_tabs import models

if TYPE_CHECKING:
    from typing import ClassVar


class LazyTabsForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.LazyTabs
        exclude: ClassVar = []


class LazyTabsListFilterForm(forms.Form):
    search = forms.CharField(required=False)
