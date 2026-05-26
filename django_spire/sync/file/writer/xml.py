from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent

from django_spire.contrib.sync.file.exceptions import FileSyncParameterError
from django_spire.contrib.sync.file.reader.xml import XmlField, XmlListField
from django_spire.contrib.sync.file.writer.base import Writer


class XmlWriter(Writer):
    def __init__(
        self,
        root_tag: str,
        record_tag: str,
        fields: list[XmlField | XmlListField],
        encoding: str = 'utf-8',
    ) -> None:
        if not root_tag:
            message = 'root_tag must not be empty'
            raise FileSyncParameterError(message)

        if not record_tag:
            message = 'record_tag must not be empty'
            raise FileSyncParameterError(message)

        if not fields:
            message = 'fields must not be empty'
            raise FileSyncParameterError(message)

        self._root_tag = root_tag
        self._record_tag = record_tag
        self._encoding = encoding
        self._fields: list[XmlField] = []
        self._list_fields: list[XmlListField] = []

        for f in fields:
            if isinstance(f, XmlListField):
                self._list_fields.append(f)
            else:
                self._fields.append(f)

    def _ensure_parent(self, element: Element, path_parts: list[str]) -> Element:
        current = element

        for part in path_parts:
            child = current.find(part)

            if child is None:
                child = SubElement(current, part)

            current = child

        return current

    def _set_field(self, element: Element, path: str, value: Any) -> None:
        parts = path.split('/')
        parent = self._ensure_parent(element, parts[:-1])
        leaf = SubElement(parent, parts[-1])
        leaf.text = str(value) if value is not None else ''

    def _set_list_field(self, element: Element, path: str, values: list[Any]) -> None:
        parts = path.split('/')
        parent = self._ensure_parent(element, parts[:-1])

        for value in values:
            item = SubElement(parent, parts[-1])
            item.text = str(value) if value is not None else ''

    def write(self, file_path: str | Path, records: list[dict[str, Any]]) -> None:
        file_path = Path(file_path)
        root = Element(self._root_tag)

        for record in records:
            element = SubElement(root, self._record_tag)

            for field in self._fields:
                value = record.get(field.key, field.default)
                self._set_field(element, field.path, value)

            for field in self._list_fields:
                values = record.get(field.key, [])
                self._set_list_field(element, field.path, values)

        tree = ElementTree(root)
        indent(tree, space='  ')
        tree.write(str(file_path), encoding=self._encoding, xml_declaration=True)
