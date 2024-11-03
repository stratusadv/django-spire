from __future__ import annotations

from django import forms

from django_spire.comment import models
from django_spire.comment.widgets import TaggingWidget


class TaggingField(forms.JSONField):
    user_list_func = None

    def __init__(self, user_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = TaggingWidget(user_list)


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = ['information']
