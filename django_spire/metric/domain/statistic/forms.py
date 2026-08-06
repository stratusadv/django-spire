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


class StatisticGroupForm(forms.ModelForm):
    @Glue.attribute(access=Glue.Access.CHANGE)
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
    @Glue.attribute(access=Glue.Access.CHANGE)
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
        fields = ['group', 'name', 'interval']
        exclude: ClassVar = []
