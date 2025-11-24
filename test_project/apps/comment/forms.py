from __future__ import annotations

from typing import ClassVar

from django import forms

from test_project.apps.comment import models


class CommentExampleForm(forms.ModelForm):
    field = forms.JSONField(required=False)

    class Meta:
        model = models.Comment
        fields: ClassVar = []
