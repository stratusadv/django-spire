from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.http import HttpRequest
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.metric.domain.statistic import models

if TYPE_CHECKING:
    from typing import ClassVar
    from uuid import UUID


class StatisticGroupForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            group, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect_url': reverse(
                        viewname='django_spire:metric:domain:statistic:page:group_detail',
                        kwargs={'pk': group.pk},
                    )
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.StatisticGroup
        fields = ['domain', 'name', 'description']
        exclude: ClassVar = []


class StatisticForm(forms.ModelForm):
    key = forms.UUIDField(
        required=False,
        help_text='Must be a UUID4. Leave blank to automatically use a UUID4.',
        error_messages={'invalid': 'Enter a valid UUID4.'},
    )

    def clean_key(self) -> UUID:
        key = self.cleaned_data.get('key')

        if key is None:
            key = self.instance.key
        elif key.version != 4:
            message = 'Key must be a UUID4.'
            raise forms.ValidationError(message)

        queryset = models.Statistic.objects.filter(key=key)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            message = 'A statistic with this key already exists.'
            raise forms.ValidationError(message)

        return key

    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            statistic, _ = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect_url': reverse(
                        viewname='django_spire:metric:domain:statistic:page:group_detail',
                        kwargs={'pk': statistic.group.pk},
                    )
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.Statistic
        fields = ['key', 'group', 'name', 'interval', 'value_type']
        exclude: ClassVar = []
