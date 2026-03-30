from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from django import forms

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class ConfirmationForm(forms.Form):
    should_confirm = forms.BooleanField(required=False)

    def __init__(self, *args, obj = None, field = [], **kwargs):
        if obj is None:
            message = 'Passing an object to ConfirmationForm is required.'
            raise ValueError(message)

        self.obj = obj

        super().__init__(*args, **kwargs)

    def save(
        self,
        user: User,
        verbs: tuple,
        activity_func: Callable | None = None,
        auto_add_activity: bool = True,
        data: dict = None,
    ):
        if data:
            for field, value in data.items():
                setattr(self.obj, field, value)
            self.obj.save()

        if activity_func is not None:
            activity_func()
        elif hasattr(self.obj, 'add_activity') and auto_add_activity:
            self.obj.add_activity(
                user=user,
                verb=verbs[1],
                information=f'{user.get_full_name()} {verbs[1].lower()} {self.obj._meta.verbose_name} "{self.obj}".'
            )


class DeleteConfirmationForm(forms.Form):
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
        auto_add_activity: bool = True,
        data: dict = None,
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
