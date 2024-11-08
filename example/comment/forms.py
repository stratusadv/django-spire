from __future__ import annotations

from typing_extensions import ClassVar

from django import forms

from example.comment import models


class CommentExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Comment
        fields: ClassVar = []
