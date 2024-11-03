from __future__ import annotations

from typing_extensions import Callable, TYPE_CHECKING

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class DeleteConfirmationForm(forms.Form):
    should_delete = forms.BooleanField(required=True)

    def __init__(self, *args, obj=None, **kwargs):
        if obj is None:
            message = 'Passing an object to DeleteConfirmationForm is required.'
            raise ValueError(message)

        self.obj = obj

        super().__init__(*args, **kwargs)

    def save(
            self,
            user: User,
            verbs: tuple,
            delete_func: Callable | None = None,
            activity_func: Callable | None = None,
            auto_add_activity: bool = True
    ) -> None:
        if delete_func is not None:
            delete_func()
        else:
            self.obj.set_deleted()

        if activity_func is not None:
            activity_func()
        elif hasattr(self.obj, 'add_activity') and auto_add_activity:
            self.obj.add_activity(
                user=user,
                verb=verbs[1],
                information=f'{user.get_full_name()} {verbs[1].lower()} {self.obj._meta.verbose_name} "{self.obj}".'
            )


class ConfirmationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.helper.layout = Layout()
        self.helper.add_input(
            Submit(
                'submit',
                'Confirm',
                css_class='btn-success btn-sm mt-1 mb-0'
            )
        )
