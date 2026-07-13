from __future__ import annotations

from django import forms
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from django_glue import GlueResponse
from django_glue.form.form import GlueModelForm

from test_project.app.rest.models import Pirate


class PirateModelForm(forms.ModelForm):
    class Meta:
        model = Pirate
        fields = ['first_name', 'last_name', 'email', 'username']


class PirateGlueModelForm(GlueModelForm):
    def process(self, request: WSGIRequest, **kwargs) -> GlueResponse:
        if self.is_valid():
            pirate = Pirate.objects.create(**self.cleaned_data)
            return GlueResponse(
                result={'redirect_url': reverse('rest:page:detail', kwargs={'pk': pirate.pk})}
            )

    class Meta:
        model = Pirate
        fields = ['first_name', 'last_name', 'email', 'username']
