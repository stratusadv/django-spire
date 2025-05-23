from typing import ClassVar

from django import forms
from django.contrib.auth.models import User

from django_spire.help_desk.models import HelpDeskTicket


class HelpDeskTicketForm(forms.ModelForm):
    def save(self, commit: bool = True, user: User | None = None) -> HelpDeskTicket:
        if user is not None:
            self.instance.created_by = user

        return super().save(commit=commit)

    class Meta:
        model = HelpDeskTicket
        exclude: ClassVar[list] = ['created_by', 'status']
