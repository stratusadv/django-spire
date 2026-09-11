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


class DomainForm(ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if self.is_valid():
            domain, _created = self.instance.services.save_model_obj(**self.cleaned_data)

            return GlueResponse(
                result={
                    'redirect': {
                        'url': reverse(viewname='django_spire:metric:domain:page:detail', kwargs={'pk': domain.pk})
                    }
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.Domain
        fields = ['name', 'description', 'sub_domain_name']
        exclude: ClassVar = []


class SubDomainForm(ModelForm):
    key = forms.SlugField(
        required=False, label='Key', help_text='Leave blank to automatically generate a slug from the name.'
    )

    def clean_key(self) -> str:
        key = self.cleaned_data.get('key')

        if not key and self.instance.pk:
            key = self.instance.key
        elif not key:
            return ''

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
                    'redirect': {
                        'url': reverse(
                            viewname='django_spire:metric:domain:page:detail',
                            kwargs={'pk': subdomain.domain.id},
                        )
                    }
                }
            )

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = models.SubDomain
        fields = ['domain', 'key', 'name', 'description']
