from __future__ import annotations

import csv

from pathlib import Path
from typing import Any

from django_spire.contrib.sync.file.parser.base import Parser


class CsvParser(Parser):
    def __init__(
        self,
        delimiter: str = ',',
        encoding: str = 'utf-8',
        field_map: dict[str, str] | None = None,
        type_map: dict[str, type] | None = None,
    ) -> None:
        self._delimiter = delimiter
        self._encoding = encoding
        self._field_map = field_map or {}
        self._type_map = type_map or {}

    def _cast_record(self, record: dict[str, Any]) -> dict[str, Any]:
        cast_record = dict(record)

        for key, cast in self._type_map.items():
            if key not in cast_record:
                message = (
                    f'type_map key {key!r} not found in record. '
                    f'Available keys: {sorted(cast_record)}'
                )
                raise KeyError(message)

            try:
                cast_record[key] = cast(cast_record[key])
            except (ValueError, TypeError) as exc:
                message = (
                    f'Failed to cast field {key!r} with value '
                    f'{cast_record[key]!r} to {cast.__name__}'
                )
                raise ValueError(message) from exc

        return cast_record

    def _map_record(self, record: dict[str, str]) -> dict[str, Any]:
        return {
            self._field_map.get(key, key): value
            for key, value in record.items()
        }

    def parse(self, file_path: str | Path) -> list[dict[str, Any]]:
        file_path = Path(file_path)

        with open(file_path, encoding=self._encoding, newline='') as handle:
            reader = csv.DictReader(handle, delimiter=self._delimiter)

            return [
                self._cast_record(self._map_record(row))
                for row in reader
            ]
