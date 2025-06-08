from __future__ import annotations

import logging
from abc import ABC
from typing import Any

from django.db import transaction
from django.db.models import Model
from django_spire.contrib.service.service import BaseService


class BaseModelService(BaseService, ABC):
    @property
    def model_obj_is_ready(self):
        return isinstance(self.obj, Model) and self.obj.id is not None

    @property
    def model_obj_is_new(self):
        return self.obj.id is None

    @property
    def _obj_is_valid(self) -> bool:
        return isinstance(self.obj, Model) and issubclass(self._obj_type, Model)

    @transaction.atomic
    def save_instance(self, **field_data: Any) -> tuple[Model, bool]:
        """
            Apply field_data to `instance`, validate, and persist.
            Accepts both `field` and `field_id` for FKs.
            Works for unsaved (create) and existing (update) instances.
            Skips editable = False and auto created fields.
        """
        if not field_data:
            return self.obj, False

        concrete = {
            f.name: f
            for f in self.obj._meta.get_fields()
            if f.concrete and not f.many_to_many and not f.one_to_many
        }

        fk_id_aliases = {f"{n}_id" for n, f in concrete.items() if f.many_to_one}
        allowed = set(concrete) | fk_id_aliases

        touched: list[str] = []

        for field, value in field_data.items():
            if field not in allowed:
                logging.warning(f'Field {field!r} is not valid for {self.obj.__class__.__name__}')
                continue

            model_field = concrete.get(field.rstrip("_id"), None)

            # Skip read-only / auto columns
            if model_field and (getattr(model_field, 'auto_created', False) or not model_field.editable):
                continue

            setattr(self.obj, field, value)
            touched.append(field.rstrip('_id'))

        # Validate only fields we touched
        try:
            self.obj.full_clean(exclude=[f for f in concrete if f not in touched])
        except:
            raise  # bubble up or wrap as needed

        if self.obj.pk is None:
            self.obj.save()
            created = True
        else:
            self.obj.save(update_fields=touched)
            created = False

        return self.obj, created