from __future__ import annotations

from typing import ClassVar

from django import forms
from django.forms import ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.help_desk.models import HelpDeskTicket


# class HelpDeskTicketCreateForm(forms.ModelForm):
#     class Meta:
#         model = HelpDeskTicket
#         exclude: ClassVar[list] = ['created_by', 'status']
#
#
# class HelpDeskTicketUpdateForm(forms.ModelForm):
#     class Meta:
#         model = HelpDeskTicket
#         exclude: ClassVar[list] = ['created_by']


class HelpDeskTicketModelForm(ModelForm):
    @Glue.Attribute(access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> GlueResponse:
        if len(self.data['description']) < 10:
            return GlueResponse(
                messages=[GlueMessage.warning('Your description is not long enough ... but I do care!')]
            )

        if self.is_valid():
            ticket = HelpDeskTicket.services.save_model_obj(request.user, **self.cleaned_data)

            return GlueResponse(
                result={'redirect_url': reverse('django_spire:help_desk:page:detail', kwargs={'pk': ticket.pk})}
            )

        return GlueResponse(messages=[GlueMessage.error('Hello')])

    class Meta:
        model = HelpDeskTicket
        fields = ['description', 'status', 'purpose', 'priority']
        exclude: ClassVar[list] = ['created_by']
