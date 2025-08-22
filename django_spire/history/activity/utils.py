from __future__ import annotations

from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import User
    from django_spire.history.activity.mixins import ActivityMixin


def add_form_activity(model_object: ActivityMixin, pk: int | bool, user: User) -> None:
    verb = (
        'created'
        if pk else 'updated'
    )

    information = (
        f'{user.get_full_name()} {verb} '
        f'{model_object._meta.verbose_name} "{model_object}".'
    )

    model_object.add_activity(
        user=user,
        verb=verb,
        information=information
    )
