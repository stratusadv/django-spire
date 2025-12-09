from __future__ import annotations

import logging

from abc import ABC
from typing import Generic, TypeVar

from django.db import transaction
from django.db.models import Model

from django_spire.contrib.constructor.django_model_constructor import BaseDjangoModelConstructor
from django_spire.contrib.service.exceptions import ServiceError


log = logging.getLogger(__name__)

TypeDjangoModel_co = TypeVar('TypeDjangoModel_co', bound=Model, covariant=True)


class BaseDjangoModelService(
    BaseDjangoModelConstructor[TypeDjangoModel_co],
    ABC,
    Generic[TypeDjangoModel_co]
):
    def _get_concrete_fields(self) -> dict:
        return {
            field.name: field
            for field in self.obj._meta.get_fields()
            if field.concrete and not field.many_to_many and not field.one_to_many
        }

    def _get_touched_fields(self, concrete_fields: dict, **field_data: dict) -> list[str]:
        foreign_key_id_aliases = {f"{name}_id" for name, field in concrete_fields.items() if field.many_to_one}
        allowed = set(concrete_fields) | foreign_key_id_aliases

        touched_fields: list[str] = []

        for field, value in field_data.items():
            if field not in allowed:
                log.warning(f'Field {field!r} is not valid for {self.obj.__class__.__name__}')
                continue

            model_field = concrete_fields.get(field.removesuffix("_id"), None)

            if model_field and (getattr(model_field, 'auto_created', False) or not model_field.editable):
                continue

            setattr(self.obj, field, value)

            touched_fields.append(field.removesuffix('_id'))

        return touched_fields

    def validate_model_obj(self, **field_data: dict) -> list[str]:
        concrete_fields = self._get_concrete_fields()
        touched_fields = self._get_touched_fields(concrete_fields, **field_data)

        exclude = [field for field in concrete_fields if field not in touched_fields]
        self.obj.full_clean(exclude=exclude)

        return touched_fields

    @transaction.atomic
    def save_model_obj(self, **field_data: dict) -> tuple[Model, bool]:
        new_model_obj_was_created = False

        if not field_data:
            message = f'Field data is required to save on {self.obj.__class__.__name__}'
            raise ServiceError(message)

        touched_fields = self.validate_model_obj(**field_data)

        if self.model_obj_is_new:
            new_model_obj_was_created = True
            self.obj.save()

        elif touched_fields:
            self.obj.save(update_fields=touched_fields)

        else:
            message = f'{self.obj.__class__.__name__} is not a new object or there was no touched fields to update.'
            log.warning(message)

        return self.obj, new_model_obj_was_created
