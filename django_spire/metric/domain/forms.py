from __future__ import annotations

from typing import TYPE_CHECKING

from django.forms import ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.metric.domain import models

if TYPE_CHECKING:
    from typing import ClassVar


class DomainForm(ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            domain, _created = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect_url': reverse(
                        viewname='django_spire:metric:domain:page:detail',
                        kwargs={'pk': domain.pk},
                    )
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.Domain
        fields = ['name', 'description', 'sub_domain_description']
        exclude: ClassVar = []


class SubDomainForm(ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            subdomain, _created = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect_url': reverse(
                        viewname='django_spire:metric:domain:page:detail',
                        kwargs={'pk': subdomain.domain.id},
                    )
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.SubDomain
        fields = ['name', 'description']
