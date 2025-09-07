from __future__ import annotations

import json

from django import forms
from django.contrib.auth.models import Group, User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit

from django_spire.auth.group.factories import bulk_create_groups_from_names


class GroupNamesField(forms.CharField):
    """Receives a list of group names as a json string"""

    def clean(self, value) -> list[str]:
        return json.loads(value)


class GroupNamesForm(forms.Form):
    groups = GroupNamesField(required=False)

    def save(self):
        return bulk_create_groups_from_names(self.cleaned_data['groups'])


class GroupForm(forms.ModelForm):
    pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     self.helper = FormHelper(self)
    #     self.helper.include_media = False
    #     self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary btn-sm bg-primary'))

    class Meta:
        model = Group
        exclude = ['permissions']
        widgets = {}


class GroupUserForm(forms.Form):
    users = forms.ModelMultipleChoiceField(required=False, queryset=User.objects.filter(is_active=True))

    @staticmethod
    def user_label(obj):
        return obj.get_full_name()
