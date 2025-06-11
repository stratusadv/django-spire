from __future__ import annotations

import logging
from abc import ABC

from django.db import transaction
from django.db.models import Model

from django_spire.contrib.service.exceptions import ServiceException
from django_spire.contrib.service.service import BaseService


class BaseDjangoModelService(BaseService, ABC):
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
                logging.warning(f'Field {field!r} is not valid for {self.obj.__class__.__name__}')
                continue

            model_field = concrete_fields.get(field.rstrip("_id"), None)

            if model_field and (getattr(model_field, 'auto_created', False) or not model_field.editable):
                continue

            setattr(self.obj, field, value)

            touched_fields.append(field.rstrip('_id'))

        return touched_fields


    @property
    def _model_obj_id_is_empty(self) -> bool:
        return self.obj.id is None or self.obj.id == 0 or self.obj.id == ''

    @property
    def _model_obj_pk_is_empty(self) -> bool:
        return self.obj.pk is None or self.obj.pk == 0 or self.obj.pk == ''

    @property
    def model_obj_is_created(self) -> bool:
        return self._obj_is_valid and not self.model_obj_is_new

    @property
    def model_obj_is_new(self) -> bool:
        return self._model_obj_id_is_empty or self._model_obj_pk_is_empty

    def model_obj_validate_field_data(self, **field_data: dict) -> list[str]:
        concrete_fields = self._get_concrete_fields()
        touched_fields = self._get_touched_fields(concrete_fields, **field_data)

        try:
            self.obj.full_clean(
                exclude=[field for field in concrete_fields if field not in touched_fields]
            )
        except:
            raise

        return touched_fields

    @transaction.atomic
    def model_obj_validate_field_data_and_save(self, **field_data: dict) -> bool:
        new_model_obj_was_created = False

        if not field_data:
            raise ServiceException(f'Field data is required to save on {self.obj.__class__.__name__}')

        touched_fields = self.model_obj_validate_field_data(**field_data)

        if self.model_obj_is_new:
            new_model_obj_was_created = True
            self.obj.save()

        elif touched_fields:
            self.obj.save(update_fields=touched_fields)

        else:
            logging.warning(f'{self.obj.__class__.__name__} is not a new object or there was no touched fields to update.')

        return new_model_obj_was_created

    class Meta:
        abstract = True

    @property
    def _obj_is_valid(self) -> bool:
        return super()._obj_is_valid and isinstance(self.obj, Model) and issubclass(self._obj_type, Model)

