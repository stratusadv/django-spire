from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from django_spire.core.forms import show_form_errors
from django_spire.history.utils import add_form_activity
from django_glue.glue import glue_model, glue_query_set

from django_spire.cookbook.recipe.models import Recipe
from django_spire.core.views import portal_views
from django_spire.cookbook import models, forms, factories

from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.permission.decorators import permission_required


def cookbook_delete_view(request, pk):
    cookbook = get_object_or_404(models.Cookbook, pk=pk)
    return portal_views.delete_form_view(
        request,
        obj=cookbook,
        return_url=request.GET.get('return_url', reverse('cookbook:page:list')),
    )


@permission_required('perms.cookbook.view_cookbook')
def cookbook_detail_view(request, pk):
    cookbook = get_object_or_404(models.Cookbook, pk=pk)
    context_data = {
        'cookbook': cookbook,
        'recipes': Recipe.objects.by_cookbook(pk)
    }

    return portal_views.detail_view(
        request,
        obj=cookbook,
        context_data=context_data,
        template='cookbook/page/cookbook_detail_page.html'
    )


def cookbook_form_view(request, pk):
    cookbook = get_object_or_null_obj(models.Cookbook, pk=pk)

    glue_model(request, 'cookbook', cookbook, 'view')
    glue_query_set(request,  'recipe_queryset', Recipe.objects.active(), 'view')

    if request.method == 'POST':
        form = forms.CookbookForm(request.POST, instance=cookbook)
        if form.is_valid():
            cookbook = form.save()
            factories.link_cookbook_recipes(cookbook, form.cleaned_data['linked_recipes'])
            add_form_activity(cookbook, pk, request.user)
            return redirect(request.GET.get('return_url', reverse('cookbook:page:list')))
        else:
            show_form_errors(request, form)
    else:
        form = forms.CookbookForm(instance=cookbook)

    return portal_views.form_view(
        request,
        form=form,
        obj=cookbook,
        template='cookbook/page/cookbook_form_page.html'
    )

@permission_required('perms.cookbook.view_cookbook')
def cookbook_list_view(request):
    context_data = {
        'cookbooks': models.Cookbook.objects.all()
    }

    return portal_views.list_view(
        request,
        model=models.Cookbook,
        context_data=context_data,
        template='cookbook/page/cookbook_list_page.html'
    )
