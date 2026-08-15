from __future__ import annotations

import itertools
import uuid

from datetime import timedelta
from decimal import Decimal
from typing_extensions import Any, TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models, transaction
from django.utils import timezone

if TYPE_CHECKING:
    from django.db.models import Field, Model


MAX_RELATION_DEPTH = 3
UNSUPPORTED = object()

_unique_counter = itertools.count(1)


def _text_value(field: Field, index: int) -> str:
    value = f'seed {index}'

    if field.max_length is None or len(value) <= field.max_length:
        return value

    return str(index)[-field.max_length :]


_VALUE_BUILDERS = (
    (models.EmailField, lambda _field, index: f'seed{index}@example.com'),
    (models.URLField, lambda _field, index: f'https://example.com/{index}'),
    (models.SlugField, lambda _field, index: f'seed-{index}'),
    (models.UUIDField, lambda _field, index: uuid.UUID(int=index)),
    (models.ImageField, lambda _field, _index: UNSUPPORTED),
    (models.FileField, lambda _field, index: SimpleUploadedFile(f'seed-{index}.txt', b'seed')),
    (models.CharField, _text_value),
    (models.TextField, _text_value),
    (models.BooleanField, lambda _field, _index: False),
    (models.DecimalField, lambda _field, index: Decimal(index)),
    (models.FloatField, lambda _field, index: float(index)),
    (models.IntegerField, lambda _field, index: index),
    (models.DateTimeField, lambda _field, _index: timezone.now()),
    (models.DateField, lambda _field, _index: timezone.now().date()),
    (models.TimeField, lambda _field, _index: timezone.now().time()),
    (models.DurationField, lambda _field, index: timedelta(seconds=index)),
    (models.JSONField, lambda _field, _index: {}),
    (models.BinaryField, lambda _field, _index: b''),
)


def _is_skippable(field: Field) -> bool:
    return field.null or field.blank or field.has_default()


def _scalar_value(field: Field, index: int) -> Any:
    if field.choices:
        first_choice = next(iter(field.choices))
        return first_choice[0]

    for field_type, builder in _VALUE_BUILDERS:
        if isinstance(field, field_type):
            return builder(field, index)

    return UNSUPPORTED


def _field_value(field: Field, index: int, depth: int) -> Any:
    if field.many_to_one or field.one_to_one:
        related = build_model_instance(field.related_model, depth=depth + 1)

        if related is None:
            return UNSUPPORTED

        return related

    return _scalar_value(field, index)


def _generic_foreign_keys(model_class: type[Model]) -> list[GenericForeignKey]:
    return [
        field
        for field in model_class._meta.get_fields()
        if isinstance(field, GenericForeignKey)
    ]


def _generic_field_names(model_class: type[Model]) -> set[str]:
    names = set()

    for generic_field in _generic_foreign_keys(model_class):
        names.add(generic_field.ct_field)
        names.add(generic_field.fk_field)

    return names


def _concrete_fields(model_class: type[Model]) -> list[Field]:
    return [
        field
        for field in model_class._meta.get_fields()
        if getattr(field, 'concrete', False)
        and not field.many_to_many
        and not (field.auto_created and field.primary_key)
    ]


def build_model_instance(
    model_class: type[Model],
    depth: int = 0,
    generic_target: Model | None = None,
) -> Model | None:
    if depth > MAX_RELATION_DEPTH:
        return None

    unique_index = next(_unique_counter)
    generic_names = _generic_field_names(model_class)

    values = {}

    for field in _concrete_fields(model_class):
        if field.name in generic_names or field.attname in generic_names:
            continue

        value = _field_value(field, unique_index, depth)

        if value is UNSUPPORTED:
            if not _is_skippable(field):
                return None

            continue

        values[field.name] = value

    if generic_target is not None:
        content_type = ContentType.objects.get_for_model(type(generic_target))

        for generic_field in _generic_foreign_keys(model_class):
            values[generic_field.ct_field] = content_type
            values[generic_field.fk_field] = generic_target.pk

    instance = model_class(**values)

    try:
        with transaction.atomic():
            instance.save()
    except Exception:
        return None
    else:
        return instance


def build_model_instances(
    model_class: type[Model],
    count: int,
    start_index: int = 0,
    generic_targets: list[Model] | None = None,
) -> list[Model]:
    instances = []

    for offset in range(count):
        index = start_index + offset

        generic_target = None

        if generic_targets:
            generic_target = generic_targets[index % len(generic_targets)]

        instance = build_model_instance(
            model_class,
            generic_target=generic_target,
        )

        if instance is None:
            return instances

        instances.append(instance)

    return instances
