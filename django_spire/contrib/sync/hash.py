from __future__ import annotations

import hashlib
import json

from typing import Any


class RecordHasher:
    def __init__(
        self,
        identity_field: str,
        compare_fields: list[str] | None = None,
    ) -> None:
        self._identity_field = identity_field
        self._compare_fields = compare_fields
        self._schema_tag = self._compute_schema_tag()

    def _compute_schema_tag(self) -> str:
        token = (
            ','.join(sorted(self._compare_fields))
            if self._compare_fields is not None
            else '*'
        )

        return hashlib.sha256(token.encode('utf-8')).hexdigest()[:8]

    def _canonical(self, record: dict[str, Any]) -> bytes:
        if self._compare_fields is not None:
            fields = self._compare_fields
        else:
            fields = sorted(
                k for k in record
                if k != self._identity_field
            )

        subset: dict[str, Any] = {}

        for field in fields:
            if field not in record:
                msg = f'Field {field!r} missing from record'
                raise ValueError(msg)

            subset[field] = record[field]

        try:
            return json.dumps(
                subset,
                sort_keys=True,
                ensure_ascii=True,
            ).encode('utf-8')
        except TypeError as exc:
            msg = f'Record contains non-serializable value: {exc}'
            raise TypeError(msg) from exc

    def hash(self, record: dict[str, Any]) -> str:
        body = hashlib.sha256(self._canonical(record)).hexdigest()
        return f'{self._schema_tag}:{body}'
