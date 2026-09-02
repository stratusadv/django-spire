from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from django import forms

from django_spire.api.models import ApiAccess

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class ApiAccessCreateForm(forms.ModelForm):
    class Meta:
        model = ApiAccess
        exclude: ClassVar[list] = ['hashed_key', 'key_hint']

    def __init__(self, *args: object, user: User | None = None, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.user = user

        if user is None or not user.is_superuser:
            self.fields.pop('has_super_access')

    def clean_has_super_access(self) -> bool:
        has_super_access = self.cleaned_data['has_super_access']

        if has_super_access and (self.user is None or not self.user.is_superuser):
            message = 'Only super users may grant super access.'
            raise forms.ValidationError(message)

        return has_super_access
