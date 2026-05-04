from __future__ import annotations

import logging

from typing import Any, TYPE_CHECKING

from django.db import transaction

from django_spire.contrib.sync.file.bidirectional import BidirectionalEngine
from django_spire.contrib.sync.file.engine import Engine
from django_spire.contrib.sync.file.exceptions import (
    FileSyncConfigError,
    FileSyncSourceNotFoundError,
)
from django_spire.contrib.sync.file.storage import DjangoModelStorage

if TYPE_CHECKING:
    from pathlib import Path

    from django_spire.contrib.sync.core.model import BidirectionalResult, Result
    from django_spire.contrib.sync.file.config import FileSyncConfig
    from django_spire.contrib.sync.file.reader.base import Reader
    from django_spire.contrib.sync.file.writer.base import Writer


logger = logging.getLogger(__name__)


class FileSyncServiceMixin:
    sync_config: FileSyncConfig
    sync_reader: Reader | None = None
    sync_writer: Writer | None = None

    def build_storage(
        self,
        scope: Any,
        baseline_path: Path | None = None,
    ) -> DjangoModelStorage:
        return DjangoModelStorage(
            model_label=self.sync_config.model_label,
            identity_field=self.sync_config.identity_field,
            sync_fields=self.sync_config.field_keys,
            scope_field=self.sync_config.scope_field,
            scope=scope,
            baseline_path=baseline_path,
            timestamp_field=self.sync_config.timestamp_field,
        )

    def build_unidirectional_engine(
        self, storage: DjangoModelStorage,
    ) -> Engine:
        return Engine(
            storage=storage,
            identity_field=self.sync_config.identity_field,
            deactivation_threshold=self.sync_config.deactivation_threshold,
            transaction=transaction.atomic,
        )

    def build_bidirectional_engine(
        self, storage: DjangoModelStorage,
    ) -> BidirectionalEngine:
        return BidirectionalEngine(
            storage=storage,
            identity_field=self.sync_config.identity_field,
            conflict_strategy=self.sync_config.conflict_strategy,
            deactivation_threshold=self.sync_config.deactivation_threshold,
            transaction=transaction.atomic,
        )

    def _validate_io(self, *, require_writer: bool = False) -> None:
        if self.sync_reader is None:
            message = f'{type(self).__name__}.sync_reader must be set'
            raise FileSyncConfigError(message)

        if require_writer and self.sync_writer is None:
            message = (
                f'{type(self).__name__}.sync_writer must be set '
                f'for bidirectional sync'
            )

            raise FileSyncConfigError(message)

    def _resolve_path(self, directory: Path) -> Path:
        path = directory / self.sync_config.filename

        if not path.is_file():
            message = f'file not found: {path}'
            raise FileSyncSourceNotFoundError(message)

        return path

    def sync_bidirectional(
        self, scope: Any, directory: Path,
    ) -> BidirectionalResult:
        self._validate_io(require_writer=True)

        path = self._resolve_path(directory)

        logger.info('Starting bidirectional sync from %s', path)

        storage = self.build_storage(
            scope=scope,
            baseline_path=directory / 'baseline_hashes.json',
        )

        engine = self.build_bidirectional_engine(storage)

        return engine.sync(
            path,
            reader=self.sync_reader,
            writer=self.sync_writer,
        )

    def sync_unidirectional(
        self, scope: Any, directory: Path,
    ) -> Result:
        self._validate_io()

        path = self._resolve_path(directory)

        logger.info('Starting unidirectional sync from %s', path)

        storage = self.build_storage(scope=scope)
        engine = self.build_unidirectional_engine(storage)

        return engine.sync(path, reader=self.sync_reader)
