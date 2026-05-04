from __future__ import annotations

import csv

from pathlib import Path
from typing import Any

from django_spire.contrib.sync.file.writer.base import Writer


class CsvWriter(Writer):
    def __init__(
        self,
        delimiter: str = ',',
        encoding: str = 'utf-8',
        field_map: dict[str, str] | None = None,
        fieldnames: list[str] | None = None,
    ) -> None:
        self._delimiter = delimiter
        self._encoding = encoding
        self._field_map = field_map or {}
        self._fieldnames = fieldnames

    def _map_record(self, record: dict[str, Any]) -> dict[str, Any]:
        if not self._field_map:
            return record

        return {
            self._field_map.get(key, key): value
            for key, value in record.items()
        }

    def write(self, file_path: str | Path, records: list[dict[str, Any]]) -> None:
        file_path = Path(file_path)
        mapped = [self._map_record(r) for r in records]

        fieldnames = self._fieldnames

        if fieldnames is None and mapped:
            fieldnames = list(mapped[0].keys())

        if not fieldnames:
            file_path.write_text('', encoding=self._encoding)
            return

        with open(file_path, 'w', encoding=self._encoding, newline='') as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                delimiter=self._delimiter,
            )

            writer.writeheader()
            writer.writerows(mapped)
