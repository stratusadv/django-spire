from __future__ import annotations

from django import forms

from example.cookbook.recipe.nutrition import models


class NutritionFactForm(forms.ModelForm):
    class Meta:
        model = models.NutritionFact
        exclude = ['recipe']
