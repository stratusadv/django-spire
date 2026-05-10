from __future__ import annotations

from django_spire.contrib.sync.core.exceptions import InvalidParameterError
from django_spire.contrib.sync.database.storage import SequenceRange
from django_spire.contrib.sync.django.models.sequence import SyncSequenceCounter


_DEFAULT_COUNTER_NAME = 'default'


class SyncSequenceAllocator:
    def __init__(self, counter_name: str = _DEFAULT_COUNTER_NAME) -> None:
        if not counter_name:
            message = 'counter_name must be a non-empty string'
            raise InvalidParameterError(message)

        self._counter_name = counter_name

    def _get_or_create_locked(self) -> SyncSequenceCounter:
        SyncSequenceCounter.objects.get_or_create(
            name=self._counter_name,
            defaults={'value': 0},
        )

        return (
            SyncSequenceCounter.objects
            .select_for_update()
            .get(name=self._counter_name)
        )

    def allocate(self, count: int = 1) -> SequenceRange:
        if count < 1:
            message = f'count must be >= 1, got {count}'
            raise InvalidParameterError(message)

        counter = self._get_or_create_locked()

        first_value = counter.value + 1
        last_value = counter.value + count
        counter.value = last_value
        counter.save(update_fields=['value', 'updated_at'])

        return SequenceRange(first=first_value, last=last_value)

    def current(self) -> int:
        counter = (
            SyncSequenceCounter.objects
            .filter(name=self._counter_name)
            .first()
        )

        if counter is None:
            return 0

        return counter.value

    def reconcile_to(self, value: int) -> None:
        if value < 1:
            return

        SyncSequenceCounter.objects.get_or_create(
            name=self._counter_name,
            defaults={'value': 0},
        )

        SyncSequenceCounter.objects.filter(
            name=self._counter_name,
            value__lt=value,
        ).update(value=value)
