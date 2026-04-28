from __future__ import annotations

import uuid

from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

from django.db import models


_FIELD_SERIALIZERS: dict[type, tuple[Any, Any]] = {}


def _register(
    field_type: type,
    serialize: Any,
    deserialize: Any,
) -> None:
    _FIELD_SERIALIZERS[field_type] = (serialize, deserialize)


def _serialize_bool(value: Any) -> bool:
    return bool(value)


def _deserialize_bool(value: Any) -> bool:
    return bool(value)


def _serialize_date(value: Any) -> str | None:
    if isinstance(value, (date, datetime)):
        return value.isoformat()

    return value


def _deserialize_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value

    if isinstance(value, str):
        return date.fromisoformat(value)

    return value


def _serialize_datetime(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.isoformat()

    return value


def _deserialize_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        return datetime.fromisoformat(value)

    return value


def _serialize_decimal(value: Any) -> str | None:
    if isinstance(value, Decimal):
        return str(value)

    return value


def _deserialize_decimal(value: Any) -> Decimal | None:
    if isinstance(value, Decimal):
        return value

    if isinstance(value, (str, int, float)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return value

    return value


def _serialize_duration(value: Any) -> float | None:
    if isinstance(value, timedelta):
        return value.total_seconds()

    return value


def _deserialize_duration(value: Any) -> timedelta | None:
    if isinstance(value, timedelta):
        return value

    if isinstance(value, (int, float)):
        return timedelta(seconds=value)

    return value


def _serialize_float(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)

    return value


def _deserialize_float(value: Any) -> float | None:
    if isinstance(value, (int, float, str)):
        return float(value)

    return value


def _serialize_int(value: Any) -> int | None:
    if isinstance(value, (int, float)):
        return int(value)

    return value


def _deserialize_int(value: Any) -> int | None:
    if isinstance(value, (int, float, str)):
        return int(value)

    return value


def _serialize_time(value: Any) -> str | None:
    if isinstance(value, time):
        return value.isoformat()

    return value


def _deserialize_time(value: Any) -> time | None:
    if isinstance(value, time):
        return value

    if isinstance(value, str):
        return time.fromisoformat(value)

    return value


def _serialize_uuid(value: Any) -> str | None:
    if isinstance(value, uuid.UUID):
        return str(value)

    return value


def _deserialize_uuid(value: Any) -> str | None:
    if isinstance(value, uuid.UUID):
        return str(value)

    return value


def _serialize_passthrough(value: Any) -> Any:
    return value


def _deserialize_passthrough(value: Any) -> Any:
    return value


_register(models.BooleanField, _serialize_bool, _deserialize_bool)
_register(models.NullBooleanField, _serialize_bool, _deserialize_bool)
_register(models.DateField, _serialize_date, _deserialize_date)
_register(models.DateTimeField, _serialize_datetime, _deserialize_datetime)
_register(models.DecimalField, _serialize_decimal, _deserialize_decimal)
_register(models.DurationField, _serialize_duration, _deserialize_duration)
_register(models.FloatField, _serialize_float, _deserialize_float)
_register(models.IntegerField, _serialize_int, _deserialize_int)
_register(models.BigIntegerField, _serialize_int, _deserialize_int)
_register(models.SmallIntegerField, _serialize_int, _deserialize_int)
_register(models.PositiveIntegerField, _serialize_int, _deserialize_int)
_register(models.PositiveSmallIntegerField, _serialize_int, _deserialize_int)
_register(models.PositiveBigIntegerField, _serialize_int, _deserialize_int)
_register(models.TimeField, _serialize_time, _deserialize_time)
_register(models.UUIDField, _serialize_uuid, _deserialize_uuid)
_register(models.ForeignKey, _serialize_uuid, _deserialize_uuid)
_register(models.OneToOneField, _serialize_uuid, _deserialize_uuid)


def _get_serializer(field: models.Field) -> tuple[Any, Any]:
    for field_type in type(field).__mro__:
        if field_type in _FIELD_SERIALIZERS:
            return _FIELD_SERIALIZERS[field_type]

    return _serialize_passthrough, _deserialize_passthrough


class SyncFieldSerializer:
    def __init__(self, model: type) -> None:
        self._concrete: dict[str, tuple[str, Any, Any]] = {}

        for field in model._meta.concrete_fields:
            attr_name = field.attname if field.is_relation else field.name
            serialize, deserialize = _get_serializer(field)
            self._concrete[attr_name] = (field.name, serialize, deserialize)

    def serialize(self, instance: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}

        for attr_name, (_name, serialize, _) in self._concrete.items():
            value = getattr(instance, attr_name)

            if value is not None:
                value = serialize(value)

            data[attr_name] = value

        return data

    def deserialize(self, field_data: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}

        for key, value in field_data.items():
            entry = self._concrete.get(key)

            if entry is None:
                result[key] = value
                continue

            _, _, deserialize = entry

            if value is not None:
                value = deserialize(value)

            result[key] = value

        return result
