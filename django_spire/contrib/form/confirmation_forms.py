from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from django import forms

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class ConfirmationForm(forms.Form):
    pass

class DeleteConfirmationForm(ConfirmationForm):
    should_delete = forms.BooleanField(required=False)

    def __init__(self, *args, obj = None, **kwargs):
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
