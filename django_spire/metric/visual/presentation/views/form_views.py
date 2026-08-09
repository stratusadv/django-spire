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

from django_spire.metric.visual.presentation import forms, models
from django_spire.metric.visual.presentation.navigation import PresentationNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


PRESENTATION_DETAIL_URL = 'django_spire:metric:visual:presentation:page:detail'


def _presentation_detail_url(presentation_pk: int) -> str:
    return reverse(PRESENTATION_DETAIL_URL, kwargs={'pk': presentation_pk})


@permission_required('visual_presentation.delete_presentation')
def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    presentation = get_object_or_404(models.Presentation, pk=pk)
    return_url = request.GET.get(
        'return_url', reverse('django_spire:metric:visual:presentation:page:list')
    )

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=presentation)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                presentation.set_deleted()
                presentation.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=(
                        f'{request.user.get_full_name()} deleted presentation "{presentation}".'
                    ),
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=presentation)

    nav = PresentationNavigation()
    nav.page_title = 'Delete Presentation'
    nav.breadcrumbs.add('Presentations', 'django_spire:metric:visual:presentation:page:list')
    nav.breadcrumbs.add(str(presentation))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {presentation}'
    context['form_description'] = (
        f'Are you sure you would like to delete presentation "{presentation}"?'
    )

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )


@permission_required('visual_presentation.add_presentation')
def create_view(request: WSGIRequest) -> TemplateResponse:
    return _form_view(request)


@permission_required('visual_presentation.change_presentation')
def update_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _form_view(request, pk)


def _form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    presentation = get_object_or_null_obj(models.Presentation, pk=pk)

    form = forms.PresentationModelForm(request.POST or None, instance=presentation)

    Glue.form(request, 'presentation_form', form, Glue.Access.DELETE)

    nav = PresentationNavigation()
    nav.page_title = str(presentation._meta.verbose_name.title())
    nav.breadcrumbs.add('Presentations', 'django_spire:metric:visual:presentation:page:list')
    nav.breadcrumbs.add('Edit' if presentation.pk else 'Create')
    context = nav.as_context()
    context['form'] = form
    context['form_template'] = 'django_spire/metric/visual/presentation/form/form.html'
    context['form_title'] = nav.page_title
    context['form_description'] = 'Edit' if presentation.pk else 'Create'

    return TemplateResponse(
        request, 'django_spire/metric/visual/presentation/page/form_page.html', context
    )


@permission_required('visual_presentation.add_slide')
def create_slide_view(request: WSGIRequest) -> TemplateResponse:
    return _slide_form_view(request)


@permission_required('visual_presentation.change_slide')
def update_slide_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _slide_form_view(request, pk)


def _slide_form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse | HttpResponseRedirect:
    slide = get_object_or_null_obj(models.Slide, pk=pk)

    if not slide.pk:
        presentation_pk = request.GET.get('presentation', 0)
        presentation = get_object_or_404(models.Presentation, pk=presentation_pk)
        slide.presentation_id = presentation.pk
    else:
        presentation = slide.presentation

    form = forms.SlideModelForm(request.POST or None, instance=slide)

    Glue.form(request, 'slide_form', form, Glue.Access.DELETE)

    nav = PresentationNavigation()
    nav.page_title = 'Edit Slide' if slide.pk else 'Add Slide'
    nav.breadcrumbs.add('Presentations', 'django_spire:metric:visual:presentation:page:list')
    nav.breadcrumbs.add(str(presentation), PRESENTATION_DETAIL_URL, {'pk': presentation.pk})
    nav.breadcrumbs.add('Edit Slide' if slide.pk else 'Add Slide')
    context = nav.as_context()
    context['form'] = form
    context['form_template'] = 'django_spire/metric/visual/presentation/form/slide_form.html'
    context['form_title'] = nav.page_title
    context['form_description'] = f'Slide for presentation "{presentation}".'
    context['presentation'] = presentation
    context['slide'] = slide

    return TemplateResponse(
        request, 'django_spire/metric/visual/presentation/page/form_page.html', context
    )


@permission_required('visual_presentation.delete_slide')
def delete_slide_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    slide = get_object_or_404(models.Slide.objects.select_related('presentation'), pk=pk)
    presentation = slide.presentation
    return_url = request.GET.get('return_url', _presentation_detail_url(presentation.pk))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=slide)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                slide.set_deleted()
                slide.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=(
                        f'{request.user.get_full_name()} deleted slide "{slide}" from '
                        f'presentation "{presentation}".'
                    ),
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=slide)

    nav = PresentationNavigation()
    nav.page_title = 'Delete Slide'
    nav.breadcrumbs.add('Presentations', 'django_spire:metric:visual:presentation:page:list')
    nav.breadcrumbs.add(str(presentation), PRESENTATION_DETAIL_URL, {'pk': presentation.pk})
    nav.breadcrumbs.add(str(slide))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {slide}'
    context['form_description'] = f'Are you sure you would like to delete slide "{slide}"?'

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )


@permission_required('visual_presentation.add_slidesection')
def create_section_view(request: WSGIRequest) -> TemplateResponse:
    return _section_form_view(request)


@permission_required('visual_presentation.change_slidesection')
def update_section_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _section_form_view(request, pk)


def _section_form_view(
    request: WSGIRequest, pk: int = 0
) -> TemplateResponse | HttpResponseRedirect:
    section = get_object_or_null_obj(models.SlideSection, pk=pk)

    if section.pk:
        slide = section.slide
    else:
        slide = get_object_or_404(models.Slide, pk=request.GET.get('slide', 0))
        section.slide_id = slide.pk

    presentation = slide.presentation

    form = forms.SlideSectionModelForm(request.POST or None, instance=section)

    Glue.form(request, 'section_form', form, Glue.Access.DELETE)

    nav = PresentationNavigation()
    nav.page_title = 'Edit Section' if section.pk else 'Add Section'
    nav.breadcrumbs.add('Presentations', 'django_spire:metric:visual:presentation:page:list')
    nav.breadcrumbs.add(str(presentation), PRESENTATION_DETAIL_URL, {'pk': presentation.pk})
    nav.breadcrumbs.add(str(slide))
    nav.breadcrumbs.add('Edit Section' if section.pk else 'Add Section')
    context = nav.as_context()
    context['form'] = form
    context['form_template'] = 'django_spire/metric/visual/presentation/form/section_form.html'
    context['form_title'] = nav.page_title
    context['form_description'] = f'Section for slide "{slide}".'
    context['presentation'] = presentation
    context['slide'] = slide
    context['section'] = section

    return TemplateResponse(
        request, 'django_spire/metric/visual/presentation/page/form_page.html', context
    )


@permission_required('visual_presentation.delete_slidesection')
def delete_section_view(request: WSGIRequest, pk: int) -> TemplateResponse | HttpResponseRedirect:
    section = get_object_or_404(
        models.SlideSection.objects.select_related('slide__presentation'), pk=pk
    )
    slide = section.slide
    presentation = slide.presentation
    return_url = request.GET.get('return_url', _presentation_detail_url(presentation.pk))

    if request.method == 'POST':
        form = DeleteConfirmationForm(data=request.POST, obj=section)

        if form.is_valid():
            if form.cleaned_data['should_delete']:
                section.set_deleted()
                section.add_activity(
                    user=request.user,
                    verb='deleted',
                    information=(
                        f'{request.user.get_full_name()} deleted section "{section}" from '
                        f'slide "{slide}".'
                    ),
                )

            return HttpResponseRedirect(return_url)
    else:
        form = DeleteConfirmationForm(obj=section)

    nav = PresentationNavigation()
    nav.page_title = 'Delete Section'
    nav.breadcrumbs.add('Presentations', 'django_spire:metric:visual:presentation:page:list')
    nav.breadcrumbs.add(str(presentation), PRESENTATION_DETAIL_URL, {'pk': presentation.pk})
    nav.breadcrumbs.add(str(slide))
    nav.breadcrumbs.add('Delete')
    context = nav.as_context()
    context['form'] = form
    context['form_title'] = f'Delete {section}'
    context['form_description'] = f'Are you sure you would like to delete section "{section}"?'

    return TemplateResponse(
        request, 'django_spire/page/delete_confirmation_form_page.html', context
    )
