from __future__ import annotations

import logging
from abc import ABC

from django.db import transaction
from django.db.models import Model

from django_spire.contrib.service.service import BaseService


class BaseModelService(BaseService, ABC):
    @property
    def _obj_is_valid(self) -> bool:
        return super()._obj_is_valid and isinstance(self.obj, Model) and issubclass(self._obj_type, Model)

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
        """
            Apply field_data to `instance`, validate, but do not persist.
            Accepts both `field` and `field_id` for FKs.
            Works for unsaved (create) and existing (update) instances.
            Skips editable = False and auto created fields.
        """
        concrete = {
            field.name: field
            for field in self.obj._meta.get_fields()
            if field.concrete and not field.many_to_many and not field.one_to_many
        }

        foreign_key_id_aliases = {f"{name}_id" for name, field in concrete.items() if field.many_to_one}
        allowed = set(concrete) | foreign_key_id_aliases

        touched_fields: list[str] = []

        for field, value in field_data.items():
            if field not in allowed:
                logging.warning(f'Field {field!r} is not valid for {self.obj.__class__.__name__}')
                continue

            model_field = concrete.get(field.rstrip("_id"), None)

            if model_field and (getattr(model_field, 'auto_created', False) or not model_field.editable):
                continue

            setattr(self.obj, field, value)

            touched_fields.append(field.rstrip('_id'))

        try:
            self.obj.full_clean(
                exclude=[field for field in concrete if field not in touched_fields]
            )
        except:
            raise

        return touched_fields

    @transaction.atomic
    def model_obj_validate_field_data_and_save(self, **field_data: dict) -> bool:
        new_model_obj_was_created = False

        if not field_data:
            return new_model_obj_was_created

        touched_fields = self.model_obj_validate_field_data(**field_data)

        if self.model_obj_is_new:
            self.obj.save()
            new_model_obj_was_created = True
        elif self.model_obj_is_created and touched_fields:
            self.obj.save(update_fields=touched_fields)
        else:
            logging.warning(f'Nothing to save for {self.obj.__class__.__name__}')

        return new_model_obj_was_created

    class Meta:
        abstract = True
