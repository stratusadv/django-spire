from __future__ import annotations

from django import forms

from example.cookbook import models


class CookbookForm(forms.ModelForm):
    linked_recipes = forms.JSONField(required=False)

    class Meta:
        model = models.Cookbook
        fields = ['name', 'description']
