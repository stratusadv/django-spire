from __future__ import annotations

import json

from django import forms

from examples.cookbook.recipe import factories, models


class IngredientsField(forms.CharField):
    def clean(self, value: str) -> list[dict]:
        cleaned_data = []

        if value:
            value = json.loads(value)

            for ingredient in value:
                form = IngredientForm(ingredient)

                if form.is_valid():
                    cleaned_data.append(form.cleaned_data)
                else:
                    raise forms.ValidationError(form.errors)

        return cleaned_data


class RecipeForm(forms.ModelForm):
    ingredients = IngredientsField()

    def save(self, commit: bool = True):
        recipe = super().save(commit=commit)
        factories.update_or_create_recipe_ingredients(recipe, self.cleaned_data['ingredients'])
        return recipe

    class Meta:
        model = models.Recipe
        exclude = []


class IngredientForm(forms.ModelForm):
    id = forms.IntegerField(required=False)

    class Meta:
        model = models.Ingredient
        exclude = ['recipe']
