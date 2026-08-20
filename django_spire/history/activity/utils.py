from __future__ import annotations

import itertools
import logging

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

from django_spire.history.activity.enums import ActivityVerb
from django_spire.history.activity.models import Activity

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django.contrib.auth.models import User
    from django.db.models import Manager, QuerySet

    from django_spire.history.activity.context import DeleteActivityEntry
    from django_spire.history.activity.mixins import ActivityMixin


BULK_ACTIVITY_COUNT_MAX = 100_000

log = logging.getLogger(__name__)


def actor_name(user: User) -> str:
    return user.get_full_name() or user.get_username()


def build_activity_information(instance: ActivityMixin, user: User, verb: str) -> str:
    return f'{actor_name(user)} {verb} {instance._meta.verbose_name} "{instance}".'


def add_activity(instance: ActivityMixin, user: User, verb: str) -> Activity:
    information = build_activity_information(instance, user, verb)
    return instance.add_activity(user=user, verb=verb, information=information)


def add_bulk_activity(
    instances: Iterable[ActivityMixin],
    user: User,
    verb: str,
    using: str | None = None
) -> list[Activity]:
    bounded_instances = list(itertools.islice(iter(instances), BULK_ACTIVITY_COUNT_MAX + 1))

    if len(bounded_instances) > BULK_ACTIVITY_COUNT_MAX:
        log.warning(
            'add_bulk_activity truncated "%s" activity records to the %d row cap; '
            'the audit trail for this operation is incomplete.',
            verb,
            BULK_ACTIVITY_COUNT_MAX,
        )

        bounded_instances = bounded_instances[:BULK_ACTIVITY_COUNT_MAX]

    instance_list = [
        instance
        for instance in bounded_instances
        if instance.pk is not None
    ]

    skipped_count = len(bounded_instances) - len(instance_list)

    if skipped_count > 0:
        log.warning(
            'add_bulk_activity skipped %d "%s" activity records for instances without '
            'primary keys (unsaved objects, bulk_create with ignore_conflicts, or a '
            'database backend that cannot return inserted rows).',
            skipped_count,
            verb,
        )

    if not instance_list:
        return []

    content_type = ContentType.objects.get_for_model(instance_list[0])

    activities = [
        Activity(
            content_type=content_type,
            object_id=instance.pk,
            user=user,
            verb=verb,
            information=build_activity_information(instance, user, verb)
        )
        for instance in instance_list
    ]

    return _activity_manager(using).bulk_create(activities)


def add_bulk_delete_activity(
    entries: Iterable[DeleteActivityEntry],
    user: User,
    using: str | None = None
) -> list[Activity]:
    entry_list = list(itertools.islice(iter(entries), BULK_ACTIVITY_COUNT_MAX + 1))

    if len(entry_list) > BULK_ACTIVITY_COUNT_MAX:
        log.warning(
            'add_bulk_delete_activity truncated "deleted" activity records to the '
            '%d row cap; the audit trail for this operation is incomplete.',
            BULK_ACTIVITY_COUNT_MAX,
        )

        entry_list = entry_list[:BULK_ACTIVITY_COUNT_MAX]

    if not entry_list:
        return []

    activities = [
        Activity(
            content_type=ContentType.objects.get_for_model(model),
            object_id=object_id,
            user=user,
            verb=ActivityVerb.DELETED,
            information=information
        )
        for model, object_id, information in entry_list
    ]

    return _activity_manager(using).bulk_create(activities)


def add_form_activity(model_object: ActivityMixin, pk: int | bool, user: User) -> None:
    verb = ActivityVerb.UPDATED if pk else ActivityVerb.CREATED
    add_activity(model_object, user, verb)


def _activity_manager(using: str | None) -> Manager[Activity] | QuerySet[Activity]:
    if using is None:
        return Activity.objects

    return Activity.objects.using(using)
