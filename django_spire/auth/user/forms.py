from __future__ import annotations

from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpRequest
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser


class UserForm(forms.ModelForm):
    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')

        email_matches_existing_user = AuthUser.objects.filter(
            Q(email=email) | Q(username=email)
        ).exists()

        if email_matches_existing_user and self.instance.pk is None:
            message = 'User with this email already exists.'
            raise forms.ValidationError(message)

        return email

    @Glue.attribute(access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> Glue.Response | None:
        if self.is_valid():
            user = self.instance.services.save_model_obj(request.user, **self.cleaned_data)

            return Glue.RedirectResponse(view_name='django_spire:auth:user:page:detail', pk=user.pk)

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = AuthUser
        fields = ['first_name', 'last_name', 'email', 'is_active']


class UserGroupForm(forms.ModelForm):
    @Glue.attribute(access=Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest) -> Glue.Response | None:
        if self.is_valid():
            user = self.instance
            user.groups.set(self.cleaned_data['groups'])

            return Glue.RedirectResponse(view_name='django_spire:auth:user:page:detail', pk=user.pk)

        return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

    class Meta:
        model = AuthUser
        fields = ['groups']
