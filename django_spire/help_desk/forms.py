from __future__ import annotations

from typing import ClassVar

from django import forms

from django_spire.help_desk.models import HelpDeskTicket


class HelpDeskTicketCreateForm(forms.ModelForm):
    class Meta:
        model = HelpDeskTicket
        exclude: ClassVar[list] = ['created_by', 'status']


class HelpDeskTicketUpdateForm(forms.ModelForm):
    class Meta:
        model = HelpDeskTicket
        exclude: ClassVar[list] = ['created_by']
