from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from django_spire.history.activity.context import get_current_user
from django_spire.history.activity.mixins import ActivityMixin

if TYPE_CHECKING:
    from django.db import models


_processing: ContextVar[bool] = ContextVar('_processing', default=False)


def _create_activity(instance: models.Model, verb: str) -> None:
    user = get_current_user()

    if not user:
        return

    information = (
        f'{user.get_full_name()} {verb} '
        f'{instance._meta.verbose_name} "{instance}".'
    )

    token = _processing.set(True)

    try:
        instance.add_activity(
            user=user,
            verb=verb,
            information=information
        )
    finally:
        _processing.reset(token)


@receiver(post_delete)
def create_activity_on_delete(
    sender: type[models.Model],
    instance: models.Model,
    **kwargs
) -> None:
    if _processing.get() or not isinstance(instance, ActivityMixin):
        return

    _create_activity(instance, 'deleted')


@receiver(post_save)
def create_activity_on_save(
    sender: type[models.Model],
    instance: models.Model,
    created: bool,
    raw: bool = False,
    **kwargs
) -> None:
    if raw or _processing.get() or not isinstance(instance, ActivityMixin):
        return

    _create_activity(instance, 'created' if created else 'updated')
