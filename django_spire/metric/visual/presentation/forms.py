from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.http import HttpRequest
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.metric.visual.presentation import models

if TYPE_CHECKING:
    from typing import ClassVar


def _presentation_detail_url(kwargs_pk: int) -> str:
    return reverse('django_spire:metric:visual:presentation:page:detail', kwargs={'pk': kwargs_pk})


class PresentationModelForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            presentation, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={'redirect': {'url': _presentation_detail_url(presentation.pk)}}
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.Presentation
        fields = ['name', 'description']
        exclude: ClassVar = []


class SlideModelForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            slide, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={'redirect': {'url': _presentation_detail_url(slide.presentation_id)}}
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    def clean(self) -> dict:
        cleaned_data = super().clean()

        presentation = cleaned_data.get('presentation')
        order = cleaned_data.get('order')

        if presentation is not None and order is not None:
            queryset = models.Slide.objects.filter(presentation=presentation, order=order)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                self.add_error(
                    'order', 'A slide with this order already exists in this presentation.'
                )

        return cleaned_data

    class Meta:
        model = models.Slide
        fields = ['presentation', 'name', 'order']
        exclude: ClassVar = []
        widgets = {'order': forms.NumberInput(attrs={'min': 0})}


class SlideSectionModelForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            section, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect': {'url': _presentation_detail_url(section.slide.presentation_id)}
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.SlideSection
        fields = ['slide', 'visual', 'row', 'col']
        exclude: ClassVar = []
        widgets = {
            'row': forms.NumberInput(attrs={'min': 0}),
            'col': forms.NumberInput(attrs={'min': 0, 'max': 11}),
        }
