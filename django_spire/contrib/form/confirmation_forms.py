from __future__ import annotations

import warnings

from typing import Callable, TYPE_CHECKING

from django import forms

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class ConfirmationForm(forms.Form):
    should_confirm = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, obj=None, field=[], **kwargs):
        if obj is None:
            message = 'Passing an object to ConfirmationForm is required.'
            raise ValueError(message)

        self.obj = obj

        super().__init__(*args, **kwargs)

    def save(
        self,
        user: User | None = None,
        verbs: tuple | None = None,
        confirmation_func: Callable | None = None,
        activity_func: Callable | None = None,
        auto_add_activity: bool | None = None,
    ) -> None:
        _warn_removed_activity_arguments(verbs, auto_add_activity)

        if confirmation_func is not None:
            confirmation_func()

        _call_deprecated_activity_func(activity_func)


class DeleteConfirmationForm(forms.Form):
    should_delete = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, obj=None, **kwargs):
        if obj is None:
            message = 'Passing an object to DeleteConfirmationForm is required.'
            raise ValueError(message)

        self.obj = obj

        super().__init__(*args, **kwargs)

    def save(
        self,
        user: User | None = None,
        verbs: tuple | None = None,
        delete_func: Callable | None = None,
        activity_func: Callable | None = None,
        auto_add_activity: bool | None = None,
    ) -> None:
        _warn_removed_activity_arguments(verbs, auto_add_activity)

        if delete_func is not None:
            delete_func()
        else:
            self.obj.set_deleted()

        _call_deprecated_activity_func(activity_func)


def _call_deprecated_activity_func(activity_func: Callable | None) -> None:
    if activity_func is None:
        return

    warnings.warn(
        'The activity_func argument is deprecated; standard activity records '
        'are created by the activity signals. activity_func was still invoked '
        'for its side effects.',
        DeprecationWarning,
        stacklevel=3,
    )

    activity_func()


def _warn_removed_activity_arguments(
    verbs: tuple | None,
    auto_add_activity: bool | None,
) -> None:
    if verbs is None and auto_add_activity is None:
        return

    warnings.warn(
        'The verbs and auto_add_activity arguments are ignored; activity '
        'records are created by the activity signals.',
        DeprecationWarning,
        stacklevel=3,
    )
