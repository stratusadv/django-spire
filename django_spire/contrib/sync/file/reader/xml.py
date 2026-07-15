from __future__ import annotations

import logging

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TYPE_CHECKING

import defusedxml.ElementTree as DefusedET

from django_spire.contrib.sync.file.exceptions import (
    FileSyncParameterError,
    FileSyncParseError,
)
from django_spire.contrib.sync.file.reader.base import Reader

if TYPE_CHECKING:
    from xml.etree.ElementTree import Element


logger = logging.getLogger(__name__)


@dataclass
class XmlField:
    key: str
    path: str
    cast: type = str
    default: str = ''
    cast_fallback_to_default: bool = False


@dataclass
class XmlListField:
    key: str
    path: str


class XmlReader(Reader):
    def __init__(
        self,
        record_path: str,
        fields: list[XmlField | XmlListField],
    ) -> None:
        self._fields: list[XmlField] = []
        self._list_fields: list[XmlListField] = []
        self._record_path = record_path

        for f in fields:
            if isinstance(f, XmlListField):
                self._list_fields.append(f)
            else:
                self._validate_field_default(f)
                self._fields.append(f)

    @staticmethod
    def _validate_field_default(f: XmlField) -> None:
        try:
            f.cast(f.default)
        except (ValueError, TypeError) as exc:
            message = (
                f'XmlField {f.key!r} default {f.default!r} '
                f'cannot be cast to {f.cast.__name__}'
            )

            raise FileSyncParameterError(message) from exc

    def _extract_text(self, element: Element, path: str, default: str = '') -> str:
        child = element.find(path)

        if child is not None and child.text:
            return child.text.strip()

        return default

    def _parse_record(self, element: Element) -> dict[str, Any]:
        record: dict[str, Any] = {}

        for f in self._fields:
            text = self._extract_text(element, f.path, f.default)

            try:
                record[f.key] = f.cast(text)
            except (ValueError, TypeError) as exc:
                if not f.cast_fallback_to_default:
                    message = (
                        f'Failed to cast field {f.key!r} with value '
                        f'{text!r} to {f.cast.__name__}'
                    )

                    raise FileSyncParseError(message) from exc

                logger.warning(
                    'Cast failed for field %r with value %r; '
                    'falling back to default %r',
                    f.key,
                    text,
                    f.default,
                )

                record[f.key] = f.cast(f.default)

        for f in self._list_fields:
            elements = element.findall(f.path)

            record[f.key] = [
                el.text.strip()
                for el in elements
                if el.text
            ]

        return record

    def read(self, file_path: str | Path) -> list[dict[str, Any]]:
        tree = DefusedET.parse(Path(file_path))
        root = tree.getroot()

        return [
            self._parse_record(element)
            for element in root.findall(self._record_path)
        ]
