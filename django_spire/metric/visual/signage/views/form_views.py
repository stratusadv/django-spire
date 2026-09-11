from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django_glue import Glue

from django_spire.contrib.form.confirmation_forms import DeleteConfirmationForm
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.metric.visual.signage import forms, models
from django_spire.metric.visual.signage.navigation import SignageNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

SIGNAGE_DETAIL_URL = 'django_spire:metric:visual:signage:page:detail'


def _signage_detail_url(signage_pk: int) -> str:
    return reverse(SIGNAGE_DETAIL_URL, kwargs={'pk': signage_pk})


def _signage_breadcrumbs(nav: SignageNavigation, signage: models.Signage) -> None:
    nav.breadcrumbs.add(str(signage), SIGNAGE_DETAIL_URL, {'pk': signage.pk})


@permission_required('django_spire_metric_visual_signage.delete_signage')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    signage = get_object_or_404(models.Signage, pk=pk)
    return_url = request.GET.get(
        'return_url', reverse('django_spire:metric:visual:signage:page:list')
    )

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=signage)

        if form.is_valid():
            form.save(user=request.user, delete_func=signage.set_deleted)

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=signage)

    nav = SignageNavigation()
    nav.page_title = 'Delete Signage'
    nav.breadcrumbs.add(
        str(signage),
        view_name='django_spire:metric:visual:signage:page:detail',
        view_kwargs={'pk': pk},
    )
    nav.breadcrumbs.add('Delete')

    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {signage}'
    context['return_url'] = return_url

    return TemplateResponse(
        request,
        'django_spire/metric/visual/signage/form/delete_confirmation_form_page.html',
        context,
    )


@permission_required('django_spire_metric_visual_signage.add_signage')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('django_spire_metric_visual_signage.change_signage')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    signage = get_object_or_null_obj(models.Signage, pk=pk)

    form = forms.SignageModelForm(request.POST or None, instance=signage)

    Glue.form(request, 'signage_form', form, Glue.Access.DELETE)

    nav = SignageNavigation()
    nav.set_page_title_to_form_action_from_model_instance(signage)

    if signage.pk:
        nav.breadcrumbs.add(
            name=str(signage),
            view_name='django_spire:metric:visual:signage:page:detail',
            view_kwargs={'pk': pk},
        )

    nav.breadcrumbs.add('Edit' if signage.pk else 'New Signage')

    context = nav.as_context()
    context['form'] = form
    context['form_template'] = 'django_spire/metric/visual/signage/form/form.html'
    context['form_title'] = nav.page_title

    return TemplateResponse(
        request, 'django_spire/metric/visual/signage/page/form_page.html', context
    )


@permission_required('django_spire_metric_visual_signage.add_signagepresentation')
def create_link_view(request: WSGIRequest, signage_pk: int) -> TemplateResponse:
    return _link_form_view(request, signage_pk=signage_pk)


@permission_required('django_spire_metric_visual_signage.change_signagepresentation')
def update_link_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _link_form_view(request, pk)


def _link_form_view(
        request: WSGIRequest, pk: int = 0, signage_pk: int = 0
) -> TemplateResponse | HttpResponseRedirect:
    link = get_object_or_null_obj(models.SignagePresentation, pk=pk)

    if link.pk:
        signage = link.signage
    else:
        signage = get_object_or_404(models.Signage, pk=signage_pk)
        link.signage_id = signage.pk

    form = forms.SignagePresentationModelForm(request.POST or None, instance=link)

    Glue.form(request, 'signage_presentation_form', form, Glue.Access.DELETE)

    nav = SignageNavigation()
    nav.set_page_title_to_form_action_from_model_instance(link)
    _signage_breadcrumbs(nav, signage)

    if link.pk:
        nav.breadcrumbs.add(
            name=str(link.presentation),
            view_name='django_spire:metric:visual:signage:page:detail',
            view_kwargs={'pk': signage.pk},
        )

    nav.breadcrumbs.add('Edit' if link.pk else 'New Presentation')

    context = nav.as_context()
    context['form'] = form
    context['form_template'] = 'django_spire/metric/visual/signage/form/link_form.html'
    context['form_title'] = nav.page_title
    context['form_description'] = f'Presentation for signage "{signage}".'
    context['signage'] = signage
    context['link'] = link

    return TemplateResponse(
        request, 'django_spire/metric/visual/signage/page/form_page.html', context
    )


@permission_required('django_spire_metric_visual_signage.delete_signagepresentation')
def delete_link_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    link = get_object_or_404(
        models.SignagePresentation.objects.select_related('signage', 'presentation'), pk=pk
    )
    signage = link.signage
    return_url = request.GET.get('return_url', _signage_detail_url(signage.pk))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=link)

        if form.is_valid():
            form.save(user=request.user, delete_func=link.set_deleted)

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=link)

    nav = SignageNavigation()
    nav.page_title = 'Delete Presentation'
    _signage_breadcrumbs(nav, signage)
    nav.breadcrumbs.add('Delete')

    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {link}'
    context['return_url'] = return_url

    return TemplateResponse(
        request,
        'django_spire/metric/visual/signage/form/delete_confirmation_form_page.html',
        context,
    )
