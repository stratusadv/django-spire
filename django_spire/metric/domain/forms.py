from __future__ import annotations

from typing import TYPE_CHECKING

# from django import forms
from django.forms import ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.metric.domain import models

if TYPE_CHECKING:
    from typing import ClassVar


class DomainForm(ModelForm):
    @Glue.attribute(access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if len(self.data['name']) < 2:
            return GlueResponse(
                messages=[
                    GlueMessage.warning('Your domain name is not long enough ... but I do care!')
                ]
            )

        if self.is_valid():
            domain = self.instance.services.save_model_obj(request.user, **self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect_url': reverse(
                        viewname='django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk}
                    )
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Hello')])

    class Meta:
        model = models.Domain
        fields = ['name', 'description', 'sub_domain_description']
        exclude: ClassVar = []


class SubDomainForm(ModelForm):
    # field = forms.JSONField(required=False)

    class Meta:
        model = models.SubDomain
        exclude: ClassVar = ['domain']
