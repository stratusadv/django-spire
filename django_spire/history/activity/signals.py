from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from django_spire.history.activity.context import get_current_user
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.activity.utils import add_activity

if TYPE_CHECKING:
    from django.db import models


@receiver(post_delete)
def create_activity_on_delete(
    sender: type[models.Model],
    instance: models.Model,
    **kwargs
) -> None:
    if not isinstance(instance, ActivityMixin):
        return

    user = get_current_user()

    if not user:
        return

    add_activity(instance, user, 'deleted')


@receiver(post_save)
def create_activity_on_save(
    sender: type[models.Model],
    instance: models.Model,
    created: bool,
    raw: bool = False,
    **kwargs
) -> None:
    if raw or not isinstance(instance, ActivityMixin):
        return

    user = get_current_user()

    if not user:
        return

    add_activity(instance, user, 'created' if created else 'updated')
