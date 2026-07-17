from __future__ import annotations

from django import forms
from django.urls import reverse
from django_glue import GlueResponse, Glue

from test_project.app.rest.models import Pirate
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.http import HttpRequest


class PirateModelForm(forms.ModelForm):
    @Glue.attribute(access=Glue.Access.CHANGE)
    def process(self, request: HttpRequest, **kwargs) -> GlueResponse | None:
        if self.is_valid():
            pirate = Pirate.services.save_model_obj(**self.cleaned_data)
            return GlueResponse(
                result={'redirect_url': reverse('rest:page:detail', kwargs={'pk': pirate.pk})}
            )

        return None

    class Meta:
        model = Pirate
        fields = ['first_name', 'last_name', 'email', 'username']
