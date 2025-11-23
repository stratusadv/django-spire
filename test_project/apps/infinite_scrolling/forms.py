from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from test_project.apps.infinite_scrolling import models

if TYPE_CHECKING:
    from typing import ClassVar


class InfiniteScrollingForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.InfiniteScrolling
        exclude: ClassVar = []
