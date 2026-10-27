from __future__ import annotations

from typing import ClassVar

from django import forms

from test_project.app.comment import models


class CommentExampleForm(forms.ModelForm):
    class Meta:
        model = models.CommentExample
        fields: ClassVar = ['name', 'description']
