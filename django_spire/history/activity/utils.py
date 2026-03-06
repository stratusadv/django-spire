from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import User

    from django_spire.history.activity.mixins import ActivityMixin
    from django_spire.history.activity.models import Activity


def add_activity(instance: ActivityMixin, user: User, verb: str) -> Activity:
    information = (
        f'{user.get_full_name()} {verb} '
        f'{instance._meta.verbose_name} "{instance}".'
    )

    return instance.add_activity(
        user=user,
        verb=verb,
        information=information
    )


def add_form_activity(model_object: ActivityMixin, pk: int | bool, user: User) -> None:
    verb = (
        'created'
        if pk else 'updated'
    )

    add_activity(model_object, user, verb)
