from __future__ import annotations

from django import forms
from django.contrib.auth.models import User

from django_spire.auth.user.models import AuthUser
from django_spire.auth.user.factories import register_new_user


class UserForm(forms.ModelForm):
    def save(self, commit: bool = True):
        self.instance.username = self.cleaned_data['email']
        return super().save(commit=commit)

    class Meta:
        model = AuthUser
        fields = ['first_name', 'last_name', 'email', 'is_active']


class AddUserForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #
    #     self.helper = FormHelper(self)
    #     self.helper.include_media = False
    #
    #     self.fields['first_name'].required = True
    #     self.fields['last_name'].required = True
    #     self.fields['email'].required = True
    #
    #     self.helper.layout = Layout(
    #         Row(
    #             Column('first_name', css_class='form-group col-md-6 col-12'),
    #             Column('last_name', css_class='form-group col-md-6 col-12')
    #         ),
    #         Row(
    #             Column(Field('email', autocomplete='off'), css_class='form-group col-md-6 col-12'),
    #             Column(Field('password', autocomplete='off'), css_class='form-group col-md-6 col-12'),
    #         ),
    #     )
    #     self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary btn-sm bg-blue'))

    class Meta:
        model = User
        exclude = ['date_joined', 'last_login', 'id', 'username']
        widgets = {
            'password': forms.PasswordInput()
        }


class UserGroupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        from django.contrib.auth.models import Group
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.include_media = False

        user_groups = self.user.groups.all()

        self.fields['group_list'] = forms.ModelMultipleChoiceField(
            queryset=Group.objects.exclude(pk__in=[group.pk for group in user_groups]),
            initial=user_groups,
            required=True,
            label='Available Groups'
        )

        self.helper.layout = Layout(
            Row(
                Column('group_list', css_class='form-group col-12'),
            ),
        )
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary btn-sm bg-blue'))


class EditUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class RegisterUserForm(forms.ModelForm):
    def clean_password(self) -> str:
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            message = 'Must be at least 8 characters long.'
            raise forms.ValidationError(message)

        return password

    def save(self, commit: bool = False):
        return register_new_user(**self.cleaned_data)

    class Meta:
        model = AuthUser
        fields = ['email', 'password', 'first_name', 'last_name']
