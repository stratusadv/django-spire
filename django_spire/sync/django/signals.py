from __future__ import annotations

import logging

from typing import Any, TYPE_CHECKING

from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete

from django_spire.sync.core.exceptions import InvalidParameterError
from django_spire.sync.django.queryset import _is_bypassed, sync_bypass

if TYPE_CHECKING:
    from django_spire.sync.django.mixin import SyncableMixin


logger = logging.getLogger(__name__)

_TRACKED_ACTIONS = frozenset({'post_add', 'post_remove', 'post_clear'})


def _find_field_name(
    model: type,
    through: type,
) -> str | None:
    for field in model._meta.many_to_many:
        if field.remote_field.through is through:
            return field.name

    return None


def _stamp_forward(
    instance: SyncableMixin,
    field_name: str,
) -> None:
    from django_spire.sync.django.sequence import (  # noqa: PLC0415
        SyncSequenceAllocator,
    )

    model = type(instance)
    now = model.get_clock().now()

    with transaction.atomic(using=instance._state.db):
        row = (
            model.objects
            .using(instance._state.db)
            .select_for_update()
            .filter(pk=instance.pk)
            .values('sync_field_timestamps')
            .first()
        )

        if row is None:
            return

        sequence_last = SyncSequenceAllocator(using=instance._state.db).allocate(1).value_last

        timestamps = dict(row['sync_field_timestamps'])
        timestamps[field_name] = now

        with sync_bypass():
            (
                model.objects
                .using(instance._state.db)
                .filter(pk=instance.pk)
                .update(
                    sync_field_timestamps=timestamps,
                    sync_field_last_modified=now,
                    sync_field_sequence=sequence_last,
                    sync_field_origin_node='',
                )
            )

    instance.sync_field_timestamps = timestamps
    instance.sync_field_last_modified = now
    instance.sync_field_sequence = sequence_last
    instance.sync_field_origin_node = ''


def _stamp_reverse(
    model: type[SyncableMixin],
    primary_keys: set[Any],
    field_name: str,
    using: str | None = None,
) -> None:
    if not primary_keys:
        return

    from django_spire.sync.django.sequence import (  # noqa: PLC0415
        SyncSequenceAllocator,
    )

    now = model.get_clock().now()

    with transaction.atomic(using=using), sync_bypass():
        instances = list(
            model.objects
            .using(using)
            .select_for_update()
            .filter(pk__in=primary_keys),
        )

        if not instances:
            return

        sequence_first = SyncSequenceAllocator(using=using).allocate(len(instances)).value_first
        sequence_next = sequence_first

        for instance in instances:
            timestamps = dict(instance.sync_field_timestamps)
            timestamps[field_name] = now

            instance.sync_field_timestamps = timestamps
            instance.sync_field_last_modified = now
            instance.sync_field_sequence = sequence_next
            instance.sync_field_origin_node = ''
            sequence_next += 1

        model.objects.using(using).bulk_update(
            instances,
            [
                'sync_field_last_modified',
                'sync_field_origin_node',
                'sync_field_sequence',
                'sync_field_timestamps',
            ],
        )


def _on_many_to_many_changed(
    sender: type,
    instance: Any,
    action: str,
    reverse: bool,
    pk_set: set[Any] | None,
    **kwargs: Any,
) -> None:
    from django_spire.sync.django.mixin import SyncableMixin  # noqa: PLC0415

    if action not in _TRACKED_ACTIONS:
        return

    if _is_bypassed():
        return

    if not reverse:
        if not isinstance(instance, SyncableMixin):
            return

        field_name = _find_field_name(type(instance), sender)

        if field_name is None:
            return

        _stamp_forward(instance, field_name)

        return

    forward_model = kwargs.get('model')

    if forward_model is None:
        return

    if not issubclass(forward_model, SyncableMixin):
        return

    field_name = _find_field_name(forward_model, sender)

    if field_name is None:
        return

    if action == 'post_clear':
        logger.warning(
            'Reverse post_clear on %s via %s is not tracked; '
            'forward-side timestamps for %r will be stale until next save',
            forward_model._meta.label,
            sender._meta.label,
            field_name,
        )

        return

    _stamp_reverse(
        forward_model,
        set(pk_set or set()),
        field_name,
        using=instance._state.db
    )


def _on_syncable_delete(
    sender: type,
    instance: Any,
    **kwargs: Any,
) -> None:
    _ = sender
    _ = kwargs

    from django_spire.sync.django.mixin import SyncableMixin  # noqa: PLC0415
    from django_spire.sync.django.models.tombstone import SyncTombstone  # noqa: PLC0415
    from django_spire.sync.django.sequence import (  # noqa: PLC0415
        SyncSequenceAllocator,
    )

    if _is_bypassed():
        return

    if not isinstance(instance, SyncableMixin):
        return

    model_label = instance._meta.label
    key = str(instance.pk)

    clock = SyncableMixin.get_clock()
    timestamp = clock.now()

    with transaction.atomic(using=instance._state.db):
        sequence_last = SyncSequenceAllocator(using=instance._state.db).allocate(1).value_last

        SyncTombstone.objects.using(instance._state.db).update_or_create(
            model_label=model_label,
            record_key=key,
            defaults={
                'origin_node': '',
                'sequence': sequence_last,
                'timestamp': timestamp,
            },
        )


def register_delete_signals(
    models: list[type[SyncableMixin]],
) -> None:
    from django_spire.sync.django.mixin import SyncableMixin  # noqa: PLC0415

    for model in models:
        if not issubclass(model, SyncableMixin):
            continue

        dispatch_uid = f'syncable_delete:{model._meta.label}'

        post_delete.connect(
            _on_syncable_delete,
            sender=model,
            dispatch_uid=dispatch_uid,
        )


def register_many_to_many_signals(
    parent_models: list[type[SyncableMixin]],
) -> None:
    if not parent_models:
        message = 'parent_models must be a non-empty list'
        raise InvalidParameterError(message)

    for parent_model in parent_models:
        for field in parent_model._meta.many_to_many:
            through_model = field.remote_field.through

            dispatch_uid = (
                f'syncable_m2m:'
                f'{parent_model._meta.label}:{field.name}'
            )

            m2m_changed.connect(
                _on_many_to_many_changed,
                sender=through_model,
                dispatch_uid=dispatch_uid,
            )
