from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.urls import reverse
from django_glue import GlueResponse, Glue

from test_project.app.rest.models import Pirate

if TYPE_CHECKING:
    from django.http import HttpRequest


class PirateModelForm(forms.ModelForm):
    @Glue.attr(required_access=Glue.Access.CHANGE)
    def process(self, request: HttpRequest, **kwargs) -> GlueResponse | None:
        if self.is_valid():
            pirate, _created = Pirate.services.save_model_obj(**self.cleaned_data)
            return GlueResponse(
                result={'redirect': {
                    'url': reverse('rest:page:detail', kwargs={'pk': pirate.pk})}
                }
            )

        return None

    class Meta:
        model = Pirate
        fields = ['first_name', 'last_name', 'email', 'username']
