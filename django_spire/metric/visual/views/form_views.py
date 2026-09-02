from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.shortcuts import get_object_or_null_obj

from django_spire.metric.visual import forms, models
from django_spire.metric.visual.navigation import VisualNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


@permission_required('django_spire_metric_visual.delete_visual')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    visual = get_object_or_404(models.Visual, pk=pk)
    return_url = request.GET.get('return_url', reverse('django_spire:metric:visual:page:list'))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=visual)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                form.save(user=request.user, delete_func=visual.set_deleted)

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=visual)

    nav = VisualNavigation()
    nav.page_title = 'Delete Visual'
    nav.breadcrumbs.add('Visuals', 'django_spire:metric:visual:page:list')
    nav.breadcrumbs.add(str(visual))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {visual}'
    context['form_description'] = f'Are you sure you would like to delete visual "{visual}"?'

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )


@permission_required('django_spire_metric_visual.add_visual')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('django_spire_metric_visual.change_visual')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    visual = get_object_or_null_obj(models.Visual, pk=pk)

    form = forms.VisualModelForm(request.POST or None, instance=visual)

    Glue.form(request, 'visual_form', form, Glue.Access.DELETE)

    nav = VisualNavigation()
    nav.page_title = str(visual._meta.verbose_name.title())
    nav.breadcrumbs.add('Visuals', 'django_spire:metric:visual:page:list')
    nav.breadcrumbs.add('Edit' if visual.pk else 'Create')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = str(visual._meta.verbose_name.title())
    context['form_description'] = 'Edit' if visual.pk else 'Create'
    context['visual'] = visual

    return TemplateResponse(request, 'django_spire/metric/visual/page/form_page.html', context)


@permission_required('django_spire_metric_visual.change_visual')
def set_default_conditions_view(request: WSGIRequest, pk: int) -> HttpResponseRedirect:
    visual = get_object_or_404(models.Visual, pk=pk)

    if request.method == 'POST':
        current_value = visual.services.transformation.current_value()
        target = current_value or 100
        visual.services.factory.create_default_conditions(target=target)

    return redirect(
        request.GET.get(
            'return_url',
            reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk}),
        )
    )


@permission_required('django_spire_metric_visual.add_visual')
def create_condition_view(request: WSGIRequest, visual_pk: int) -> TemplateResponse:
    return _condition_form_view(request, visual_pk=visual_pk)


@permission_required('django_spire_metric_visual.change_visual')
def update_condition_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _condition_form_view(request, pk)


def _condition_form_view(request: WSGIRequest, pk: int = 0, visual_pk: int = 0) -> TemplateResponse:
    condition = get_object_or_null_obj(models.VisualCondition, pk=pk)

    if condition.pk:
        visual = condition.visual
    else:
        visual = get_object_or_404(models.Visual, pk=visual_pk)
        condition.visual = visual

    form = forms.VisualConditionModelForm(request.POST or None, instance=condition)

    Glue.form(request, 'visual_condition_form', form, Glue.Access.DELETE)

    nav = VisualNavigation()
    nav.page_title = 'Edit Condition' if condition.pk else 'Add Condition'
    nav.breadcrumbs.add('Visuals', 'django_spire:metric:visual:page:list')
    nav.breadcrumbs.add(str(visual), 'django_spire:metric:visual:page:detail', {'pk': visual.pk})
    nav.breadcrumbs.add('Edit Condition' if condition.pk else 'Add Condition')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = nav.page_title
    context['form_description'] = f'Conditions for visual "{visual}".'
    context['visual'] = visual
    context['condition'] = condition

    return TemplateResponse(
        request, 'django_spire/metric/visual/page/condition_form_page.html', context
    )


@permission_required('django_spire_metric_visual.delete_visual')
def delete_condition_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    condition = get_object_or_404(models.VisualCondition.objects.select_related('visual'), pk=pk)
    visual = condition.visual
    return_url = request.GET.get(
        'return_url', reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk})
    )

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=condition)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                form.save(user=request.user, delete_func=condition.set_deleted)

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=condition)

    nav = VisualNavigation()
    nav.page_title = 'Delete Condition'
    nav.breadcrumbs.add('Visuals', 'django_spire:metric:visual:page:list')
    nav.breadcrumbs.add(str(visual), 'django_spire:metric:visual:page:detail', {'pk': visual.pk})
    nav.breadcrumbs.add('Delete Condition')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {condition}'
    context['form_description'] = f'Are you sure you would like to delete condition "{condition}"?'

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )


@permission_required('django_spire_metric_visual.add_visual')
def create_reference_view(request: WSGIRequest, visual_pk: int) -> TemplateResponse:
    return _reference_form_view(request, visual_pk=visual_pk)


@permission_required('django_spire_metric_visual.change_visual')
def update_reference_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _reference_form_view(request, pk)


def _reference_choices(visual: models.Visual) -> list[str]:
    choice_set: set[str] = set(
        visual.references.order_by('reference').values_list('reference', flat=True)
    )

    if visual.statistic_id:
        choice_set.update(
            visual.statistic.values.order_by('reference')
            .values_list('reference', flat=True)
            .distinct()
        )

    return sorted(choice_set)


def _reference_form_view(request: WSGIRequest, pk: int = 0, visual_pk: int = 0) -> TemplateResponse:
    reference_obj = get_object_or_null_obj(models.VisualReference, pk=pk)

    if reference_obj.pk:
        visual = reference_obj.visual
    else:
        visual = get_object_or_404(models.Visual, pk=visual_pk)
        reference_obj.visual = visual

    form = forms.VisualReferenceModelForm(request.POST or None, instance=reference_obj)

    Glue.form(request, 'visual_reference_form', form, Glue.Access.DELETE)

    nav = VisualNavigation()

    nav.page_title = 'Edit Reference' if reference_obj.pk else 'Add Reference'
    nav.breadcrumbs.add('Visuals', 'django_spire:metric:visual:page:list')
    nav.breadcrumbs.add(str(visual), 'django_spire:metric:visual:page:detail', {'pk': visual.pk})
    nav.breadcrumbs.add(nav.page_title)

    context = nav.as_context()
    context['form'] = form
    context['form_title'] = nav.page_title
    context['form_description'] = f'References for visual "{visual}".'
    context['visual'] = visual
    context['reference'] = reference_obj
    context['reference_choices'] = _reference_choices(visual)

    return TemplateResponse(
        request, 'django_spire/metric/visual/page/reference_form_page.html', context
    )


@permission_required('django_spire_metric_visual.delete_visual')
def delete_reference_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    reference_obj = get_object_or_404(
        models.VisualReference.objects.select_related('visual'), pk=pk
    )
    visual = reference_obj.visual
    return_url = request.GET.get(
        'return_url', reverse('django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk})
    )

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=reference_obj)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                form.save(user=request.user, delete_func=reference_obj.set_deleted)

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=reference_obj)

    nav = VisualNavigation()
    nav.page_title = 'Delete Reference'
    nav.breadcrumbs.add('Visuals', 'django_spire:metric:visual:page:list')
    nav.breadcrumbs.add(str(visual), 'django_spire:metric:visual:page:detail', {'pk': visual.pk})
    nav.breadcrumbs.add('Delete Reference')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {reference_obj}'
    context['form_description'] = (
        f'Are you sure you would like to delete reference "{reference_obj}"?'
    )

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )
