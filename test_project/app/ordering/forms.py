from __future__ import annotations

from django import forms

from test_project.app.ordering import models


class DuckForm(forms.ModelForm):
    class Meta:
        model = models.Duck
        fields = ['name', 'color']
