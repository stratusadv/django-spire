from typing import Optional

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from django_spire.core.forms import show_form_errors
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.history.utils import add_form_activity
from django_glue.glue import glue_model, glue_query_set

from django_spire.cookbook.models import Cookbook
from django_spire.cookbook.recipe import models, forms
from django_spire.cookbook.recipe.nutrition.models import NutritionFact
from django_spire.core.views import portal_views


def recipe_delete_view(request, pk):
    recipe = get_object_or_404(models.Recipe, pk=pk)
    return portal_views.delete_form_view(
        request,
        obj=recipe,
        return_url=request.GET.get('return_url', reverse('recipe_list')),
    )


def recipe_detail_view(request, pk):
    recipe = get_object_or_404(models.Recipe, pk=pk)
    context_data = {
        'recipe': recipe,
        'ingredients': recipe.ingredients.active()
    }
    return portal_views.detail_view(
        request,
        obj=recipe,
        context_data=context_data,
        template='cookbook/recipe/page/recipe_detail_page.html'
    )


def recipe_form_view(request, pk, cookbook_pk: Optional[int]= None):
    if cookbook_pk is not None:
        cookbook = get_object_or_404(Cookbook, pk=cookbook_pk)

    recipe = get_object_or_null_obj(models.Recipe, pk=pk)

    if recipe.pk is None:
        ingredients = models.Ingredient.objects.none()
        nutrition_facts = NutritionFact.objects.none()
    else:
        ingredients = recipe.ingredients.active()
        nutrition_facts = recipe.nutrition_facts.active()

    glue_model(request, 'recipe', recipe, 'view')

    glue_query_set(request, 'ingredient_queryset', ingredients, 'view', exclude=['recipe'])
    glue_query_set(request, 'nutrition_facts_queryset', nutrition_facts, 'view', exclude=['recipe'])
    glue_model(request, 'ingredient_template', models.Ingredient(), 'view', exclude=['recipe'])
    glue_model(request, 'nutrition_fact_template', NutritionFact(), 'view', exclude=['recipe'])

    if request.method == 'POST':
        form = forms.RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            recipe = form.save()

            if cookbook_pk is not None:
                recipe.cookbook_recipes.create(cookbook=cookbook)

            add_form_activity(recipe, pk, request.user)
            return redirect(request.GET.get('return_url', reverse('cookbook:recipe:page:detail', kwargs={'pk': recipe.pk})))
        else:
            show_form_errors(request, form)
    else:
        form = forms.RecipeForm(instance=recipe)

    return portal_views.form_view(
        request,
        form=form,
        obj=recipe,
        template='cookbook/recipe/page/recipe_form_page.html'
    )


def recipe_list_view(request):
    context_data = {
        'recipes': models.Recipe.objects.active()
    }

    return portal_views.list_view(
        request,
        model=models.Recipe,
        context_data=context_data,
        template='cookbook/recipe/page/recipe_list_page.html'
    )
