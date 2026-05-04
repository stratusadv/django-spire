from __future__ import annotations

import contextlib
import json
import logging
import os
import tempfile

from pathlib import Path
from typing import Any, Protocol, TYPE_CHECKING

from django.apps import apps

from django_spire.contrib.sync.file.exceptions import FileSyncParameterError
from django_spire.contrib.sync.file.models import FileSyncableMixin

if TYPE_CHECKING:
    from datetime import datetime

    from django.db.models import Model, QuerySet


logger = logging.getLogger(__name__)

_HASH_FIELD = FileSyncableMixin.SYNC_HASH_FIELD
_BULK_BATCH_SIZE = 5_000


class Storage(Protocol):
    def create_many(self, records: list[dict[str, Any]], hashes: dict[str, str]) -> None: ...
    def deactivate_many(self, keys: set[str]) -> None: ...
    def get_active_keys(self) -> set[str]: ...
    def get_hashes(self, keys: set[str]) -> dict[str, str]: ...
    def get_many(self, keys: set[str]) -> dict[str, dict[str, Any]]: ...
    def update_many(self, records: list[dict[str, Any]], hashes: dict[str, str]) -> None: ...


class BidirectionalStorage(Storage, Protocol):
    def get_baseline_hashes(self) -> dict[str, str]: ...
    def get_timestamps(self, keys: set[str]) -> dict[str, datetime]: ...
    def save_baseline_hashes(self, hashes: dict[str, str]) -> None: ...


class DjangoModelStorage:
    def __init__(
        self,
        model_label: str,
        identity_field: str,
        sync_fields: tuple[str, ...],
        scope_field: str = '',
        scope: Any = None,
        baseline_path: Path | None = None,
        timestamp_field: str = 'modified_datetime',
        batch_size: int = _BULK_BATCH_SIZE,
    ) -> None:
        if not model_label:
            message = 'model_label must not be empty'
            raise FileSyncParameterError(message)

        if not identity_field:
            message = 'identity_field must not be empty'
            raise FileSyncParameterError(message)

        if not sync_fields:
            message = 'sync_fields must not be empty'
            raise FileSyncParameterError(message)

        if identity_field not in sync_fields:
            message = f'identity_field {identity_field!r} must be in sync_fields'
            raise FileSyncParameterError(message)

        if batch_size < 1:
            message = f'batch_size must be >= 1, got {batch_size}'
            raise FileSyncParameterError(message)

        self._batch_size = batch_size
        self._model_label = model_label
        self._identity_field = identity_field
        self._sync_fields = sync_fields
        self._scope_field = scope_field
        self._scope = scope
        self._baseline_path = baseline_path
        self._timestamp_field = timestamp_field

        self._update_fields = [
            f for f in self._sync_fields if f != self._identity_field
        ] + ['is_active', 'is_deleted', _HASH_FIELD]

    def _get_model(self) -> type[Model]:
        return apps.get_model(self._model_label)

    def _queryset(self) -> QuerySet:
        qs = self._get_model().objects.all()

        if self._scope is not None and self._scope_field:
            qs = qs.filter(**{self._scope_field: self._scope})

        return qs

    def _active_queryset(self) -> QuerySet:
        return self._queryset().filter(is_active=True, is_deleted=False)

    def _by_keys(self, keys: set[str]) -> QuerySet:
        return self._active_queryset().filter(
            **{f'{self._identity_field}__in': keys}
        )

    def _to_dict(self, instance: Any) -> dict[str, Any]:
        return {
            field: getattr(instance, field)
            for field in self._sync_fields
        }

    def _to_instance(self, record: dict[str, Any], hash_value: str) -> Any:
        model = self._get_model()

        kwargs = {
            'is_active': True,
            'is_deleted': False,
            _HASH_FIELD: hash_value,
        }

        if self._scope is not None and self._scope_field:
            kwargs[self._scope_field] = self._scope

        for field in self._sync_fields:
            if field in record:
                kwargs[field] = record[field]

        return model(**kwargs)

    def create_many(self, records: list[dict[str, Any]], hashes: dict[str, str]) -> None:
        if not records:
            return

        logger.info('Creating %d records in %s', len(records), self._model_label)

        instances = [
            self._to_instance(r, hashes.get(str(r[self._identity_field]), ''))
            for r in records
        ]

        model = self._get_model()

        for start in range(0, len(instances), self._batch_size):
            batch = instances[start:start + self._batch_size]

            model.objects.bulk_create(
                batch,
                update_conflicts=True,
                unique_fields=[
                    self._scope_field, self._identity_field]
                    if self._scope_field
                    else [self._identity_field
                ],
                update_fields=self._update_fields,
            )

    def deactivate_many(self, keys: set[str]) -> None:
        if not keys:
            return

        logger.info('Deactivating %d records in %s', len(keys), self._model_label)

        self._queryset().filter(
            **{f'{self._identity_field}__in': keys}
        ).update(is_active=False, is_deleted=True)

    def get_active_keys(self) -> set[str]:
        return set(
            self._active_queryset()
            .values_list(self._identity_field, flat=True)
        )

    def get_hashes(self, keys: set[str]) -> dict[str, str]:
        if not keys:
            return {}

        return dict(
            self._by_keys(keys)
            .values_list(self._identity_field, _HASH_FIELD)
        )

    def get_many(self, keys: set[str]) -> dict[str, dict[str, Any]]:
        if not keys:
            return {}

        return {
            getattr(instance, self._identity_field): self._to_dict(instance)
            for instance in self._by_keys(keys)
        }

    def update_many(self, records: list[dict[str, Any]], hashes: dict[str, str]) -> None:
        if not records:
            return

        keys = [str(r[self._identity_field]) for r in records]

        existing = {
            getattr(inst, self._identity_field): inst
            for inst in self._by_keys(set(keys))
        }

        to_update = []

        for record in records:
            key = str(record[self._identity_field])
            instance = existing.get(key)

            if instance is None:
                continue

            for field in self._sync_fields:
                if field in record:
                    setattr(instance, field, record[field])

            setattr(instance, _HASH_FIELD, hashes.get(key, ''))
            to_update.append(instance)

        if not to_update:
            return

        logger.info('Updating %d records in %s', len(to_update), self._model_label)

        model = self._get_model()
        fields = [*list(self._sync_fields), _HASH_FIELD]

        for start in range(0, len(to_update), self._batch_size):
            batch = to_update[start:start + self._batch_size]
            model.objects.bulk_update(batch, fields)

    def get_baseline_hashes(self) -> dict[str, str]:
        if self._baseline_path is None or not self._baseline_path.is_file():
            return {}

        try:
            data = json.loads(self._baseline_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning(
                'Failed to read baseline hashes from %s: %s',
                self._baseline_path, exc,
            )

            return {}

        if not isinstance(data, dict):
            logger.warning(
                'Baseline hashes in %s is not a dict, ignoring',
                self._baseline_path,
            )

            return {}

        return data

    def save_baseline_hashes(self, hashes: dict[str, str]) -> None:
        if self._baseline_path is None:
            return

        self._baseline_path.parent.mkdir(parents=True, exist_ok=True)

        content = json.dumps(hashes, indent=2, sort_keys=True)

        fd, raw_tmp_path = tempfile.mkstemp(
            dir=str(self._baseline_path.parent),
            suffix='.tmp',
        )

        tmp_path = Path(raw_tmp_path)

        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())

            tmp_path.replace(self._baseline_path)
        except BaseException:
            with contextlib.suppress(OSError):
                tmp_path.unlink()

            raise

    def get_timestamps(self, keys: set[str]) -> dict[str, datetime]:
        if not keys:
            return {}

        return dict(
            self._by_keys(keys)
            .values_list(self._identity_field, self._timestamp_field)
        )
