from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.http import HttpRequest
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.metric.visual.signage import models

if TYPE_CHECKING:
    from typing import ClassVar


def _signage_detail_url(kwargs_pk: int) -> str:
    return reverse('django_spire:metric:visual:signage:page:detail', kwargs={'pk': kwargs_pk})


class SignageModelForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            signage, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(result={'redirect': {'url': _signage_detail_url(signage.pk)}})

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.Signage
        fields = ['name', 'description', 'slide_display_seconds']
        exclude: ClassVar = []
        widgets = {'slide_display_seconds': forms.NumberInput(attrs={'min': 1})}


class SignagePresentationModelForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            link, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(result={'redirect': {'url': _signage_detail_url(link.signage_id)}})

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.SignagePresentation
        fields = ['signage', 'presentation', 'order']
        exclude: ClassVar = []
        widgets = {'order': forms.NumberInput(attrs={'min': 0})}
