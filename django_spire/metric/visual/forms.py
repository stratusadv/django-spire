from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.http import HttpRequest
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.metric.visual import models
from django_spire.metric.visual.choices import VisualConditionOperatorChoices

if TYPE_CHECKING:
    from typing import ClassVar


class VisualModelForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            visual, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect': {
                        'url': reverse(
                            'django_spire:metric:visual:page:detail', kwargs={'pk': visual.pk}
                        )
                    }
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.Visual
        fields = ['name', 'description', 'statistic', 'kind', 'date']
        exclude: ClassVar = []
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class VisualConditionModelForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            condition, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect': {
                        'url': reverse(
                            'django_spire:metric:visual:page:detail',
                            kwargs={'pk': condition.visual_id},
                        )
                    }
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    def clean(self) -> dict:
        cleaned_data = super().clean()

        operator = cleaned_data.get('operator')
        tolerance = cleaned_data.get('tolerance')

        if operator == VisualConditionOperatorChoices.BETWEEN and (
            tolerance is None or tolerance == 0
        ):
            self.add_error('tolerance', 'Tolerance is required for "At or Near Target".')

        return cleaned_data

    class Meta:
        model = models.VisualCondition
        fields = ['state', 'operator', 'target', 'tolerance', 'order']
        exclude: ClassVar = []
        widgets = {
            'target': forms.NumberInput(attrs={'step': '0.0001'}),
            'tolerance': forms.NumberInput(attrs={'step': '0.0001'}),
        }


class VisualReferenceModelForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            reference_obj, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect': {
                        'url': reverse(
                            'django_spire:metric:visual:page:detail',
                            kwargs={'pk': reference_obj.visual_id},
                        )
                    }
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    def clean(self) -> dict:
        cleaned_data = super().clean()

        pattern = cleaned_data.get('reference', '')
        statistic = self.instance.visual.statistic if self.instance.visual_id else None

        if (
            statistic
            and statistic.values.exists()
            and not statistic.values.for_reference_pattern(pattern).exists()
        ):
            self.add_error(
                'reference',
                'That reference pattern does not match any values for the selected statistic.',
            )

        return cleaned_data

    class Meta:
        model = models.VisualReference
        fields = ['reference', 'label', 'order']
        exclude: ClassVar = []
