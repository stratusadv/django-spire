from __future__ import annotations

import json

from django import forms
from django.contrib.auth.models import Group, User

from django_spire.auth.group.factories import bulk_create_groups_from_names


class GroupNamesField(forms.CharField):
    """
        Receives a list of group names as a json string
    """
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
    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.fields['available_users'] = forms.ModelMultipleChoiceField(
            queryset=User.objects.exclude(id__in=[user.id for user in group.user_set.all()]),
            required=True,
        )
        self.fields['available_users'].label_from_instance = self.user_label
        self.helper.layout = Layout(
            Row(
                Column('available_users', css_class='form-group col-12'),
            ),
        )
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary btn-sm bg-primary'))

    @staticmethod
    def user_label(obj):
        return obj.get_full_name()
