from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.forms import ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.metric.domain import models

if TYPE_CHECKING:
    from typing import ClassVar
    from uuid import UUID


class DomainForm(ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            domain, _created = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect_url': reverse(
                        viewname='django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk}
                    )
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.Domain
        fields = ['name', 'description', 'sub_domain_name']
        exclude: ClassVar = []


class SubDomainForm(ModelForm):
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

        queryset = models.SubDomain.objects.filter(key=key)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            message = 'A sub domain with this key already exists.'
            raise forms.ValidationError(message)

        return key

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
        fields = ['key', 'name', 'description']
