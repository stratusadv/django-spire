from __future__ import annotations

import logging

from typing import Any, TYPE_CHECKING

from django.db import transaction
from django.db.models.signals import m2m_changed

from django_spire.contrib.sync.core.exceptions import InvalidParameterError
from django_spire.contrib.sync.django.queryset import _is_bypassed, sync_bypass

if TYPE_CHECKING:
    from django_spire.contrib.sync.django.mixin import SyncableMixin


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
    model = type(instance)
    now = model.get_clock().now()

    with transaction.atomic():
        row = model.objects.select_for_update().filter(
            pk=instance.pk,
        ).values('sync_field_timestamps').first()

        if row is None:
            return

        timestamps = dict(row['sync_field_timestamps'])
        timestamps[field_name] = now

        model.objects.filter(pk=instance.pk).update(
            sync_field_timestamps=timestamps,
            sync_field_last_modified=now,
        )

    instance.sync_field_timestamps = timestamps
    instance.sync_field_last_modified = now


def _stamp_reverse(
    model: type[SyncableMixin],
    pks: set[Any],
    field_name: str,
) -> None:
    if not pks:
        return

    now = model.get_clock().now()

    with transaction.atomic(), sync_bypass():
        instances = list(
            model.objects.select_for_update().filter(pk__in=pks),
        )

        for instance in instances:
            timestamps = dict(instance.sync_field_timestamps)
            timestamps[field_name] = now
            instance.sync_field_timestamps = timestamps
            instance.sync_field_last_modified = now

        if instances:
            model.objects.bulk_update(
                instances,
                ['sync_field_timestamps', 'sync_field_last_modified'],
            )


def _on_m2m_changed(
    sender: type,
    instance: Any,
    action: str,
    reverse: bool,
    pk_set: set[Any] | None,
    **kwargs: Any,
) -> None:
    from django_spire.contrib.sync.django.mixin import SyncableMixin

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

    _stamp_reverse(forward_model, set(pk_set or set()), field_name)


def register_m2m_signals(
    models: list[type[SyncableMixin]],
) -> None:
    from django_spire.contrib.sync.django.mixin import SyncableMixin

    for model in models:
        if not issubclass(model, SyncableMixin):
            message = (
                f'Cannot register M2M signals for {model!r}: '
                f'must be a SyncableMixin subclass'
            )
            raise InvalidParameterError(message)

        for field in model._meta.many_to_many:
            through = field.remote_field.through

            m2m_changed.connect(
                _on_m2m_changed,
                sender=through,
                dispatch_uid=(
                    f'syncable_m2m:{model._meta.label}:{field.name}'
                ),
            )
