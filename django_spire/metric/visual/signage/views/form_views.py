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
    nav.breadcrumbs.add('Signages', 'django_spire:metric:visual:signage:page:list')
    nav.breadcrumbs.add(str(signage), SIGNAGE_DETAIL_URL, {'pk': signage.pk})


@permission_required('visual_signage.delete_signage')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    signage = get_object_or_404(models.Signage, pk=pk)
    return_url = request.GET.get(
        'return_url', reverse('django_spire:metric:visual:signage:page:list')
    )

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=signage)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                signage.set_deleted()
                signage.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=f'{request.user.get_full_name()} deleted signage "{signage}".',
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=signage)

    nav = SignageNavigation()
    nav.page_title = 'Delete Signage'
    nav.breadcrumbs.add('Signages', 'django_spire:metric:visual:signage:page:list')
    nav.breadcrumbs.add(str(signage))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {signage}'
    context['form_description'] = f'Are you sure you would like to delete signage "{signage}"?'

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )


@permission_required('visual_signage.add_signage')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('visual_signage.change_signage')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    signage = get_object_or_null_obj(models.Signage, pk=pk)

    form = forms.SignageModelForm(request.POST or None, instance=signage)

    Glue.form(request, 'signage_form', form, Glue.Access.DELETE)

    nav = SignageNavigation()
    nav.page_title = str(signage._meta.verbose_name.title())
    nav.breadcrumbs.add('Signages', 'django_spire:metric:visual:signage:page:list')
    nav.breadcrumbs.add('Edit' if signage.pk else 'Create')
    context = nav.as_context()
    context['form'] = form
    context['form_template'] = 'django_spire/metric/visual/signage/form/form.html'
    context['form_title'] = nav.page_title
    context['form_description'] = 'Edit' if signage.pk else 'Create'

    return TemplateResponse(
        request, 'django_spire/metric/visual/signage/page/form_page.html', context
    )


@permission_required('visual_signage.add_signagepresentation')
def create_link_view(request: WSGIRequest) -> TemplateResponse:
    return _link_form_view(request)


@permission_required('visual_signage.change_signagepresentation')
def update_link_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _link_form_view(request, pk)


def _link_form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse | HttpResponseRedirect:
    link = get_object_or_null_obj(models.SignagePresentation, pk=pk)

    if link.pk:
        signage = link.signage
    else:
        signage = get_object_or_404(models.Signage, pk=request.GET.get('signage', 0))
        link.signage_id = signage.pk

    form = forms.SignagePresentationModelForm(request.POST or None, instance=link)

    Glue.form(request, 'signage_presentation_form', form, Glue.Access.DELETE)

    nav = SignageNavigation()
    nav.page_title = 'Edit Presentation' if link.pk else 'Add Presentation'
    _signage_breadcrumbs(nav, signage)
    nav.breadcrumbs.add('Edit Presentation' if link.pk else 'Add Presentation')
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


@permission_required('visual_signage.delete_signagepresentation')
def delete_link_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    link = get_object_or_404(
        models.SignagePresentation.objects.select_related('signage', 'presentation'), pk=pk
    )
    signage = link.signage
    return_url = request.GET.get('return_url', _signage_detail_url(signage.pk))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=link)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                link.set_deleted()
                link.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=(
                        f'{request.user.get_full_name()} removed presentation '
                        f'"{link.presentation}" from signage "{signage}".'
                    ),
                )

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
    context['form_description'] = (
        f'Are you sure you would like to remove presentation "{link.presentation}" from '
        f'signage "{signage}"?'
    )

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )
