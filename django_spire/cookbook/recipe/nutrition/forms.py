from django import forms

from django_spire.cookbook.recipe.nutrition import models


class NutritionFactForm(forms.ModelForm):
    class Meta:
        model = models.NutritionFact
        exclude = ['recipe']

