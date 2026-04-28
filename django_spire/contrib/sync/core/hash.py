from __future__ import annotations

import hashlib
import json

from typing import Any

from django_spire.contrib.sync.core.exceptions import (
    RecordFieldError,
    RecordSerializationError,
)


class RecordHasher:
    def __init__(
        self,
        identity_field: str,
        compare_fields: list[str] | None = None,
    ) -> None:
        self._compare_fields = compare_fields
        self._identity_field = identity_field
        self._schema_tag = self._compute_schema_tag()

    def _canonical(self, record: dict[str, Any]) -> bytes:
        if self._compare_fields is not None:
            fields = self._compare_fields
        else:
            fields = sorted(
                key for key in record
                if key != self._identity_field
            )

        subset: dict[str, Any] = {}

        for field_name in fields:
            if field_name not in record:
                message = f'Field {field_name!r} missing from record'
                raise RecordFieldError(message)

            subset[field_name] = record[field_name]

        try:
            return json.dumps(
                subset,
                sort_keys=True,
                ensure_ascii=True,
            ).encode('utf-8')
        except TypeError as exception:
            message = f'Record contains non-serializable value: {exception}'
            raise RecordSerializationError(message) from exception

    def _compute_schema_tag(self) -> str:
        token = (
            ','.join(sorted(self._compare_fields))
            if self._compare_fields is not None
            else '*'
        )

        return hashlib.sha256(token.encode('utf-8')).hexdigest()[:16]

    def hash(self, record: dict[str, Any]) -> str:
        body = hashlib.sha256(self._canonical(record)).hexdigest()
        return f'{self._schema_tag}:{body}'
