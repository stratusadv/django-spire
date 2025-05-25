from typing import Any
import logging
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Model


class DefaultService:

    @staticmethod
    @transaction.atomic
    def save_instance(instance: Model, **field_data: Any) -> tuple[Model, bool]:
        """
            Apply field_data to `instance`, validate, and persist.
            Accepts both `field` and `field_id` for FKs.
            Works for unsaved (create) and existing (update) instances.
            Skips editable = False and auto created fields.
        """
        if not field_data:
            return instance, False

        concrete = {
            f.name: f
            for f in instance._meta.get_fields()
            if f.concrete and not f.many_to_many and not f.one_to_many
        }

        fk_id_aliases = {f"{n}_id" for n, f in concrete.items() if f.many_to_one}
        allowed = set(concrete) | fk_id_aliases

        touched: list[str] = []

        for field, value in field_data.items():
            if field not in allowed:
                logging.warning(f'Field {field!r} is not valid for {instance.__class__.__name__}')
                continue

            model_field = concrete.get(field.rstrip("_id"), None)

            # Skip read-only / auto columns
            if model_field and (getattr(model_field, 'auto_created', False) or not model_field.editable):
                continue

            setattr(instance, field, value)
            touched.append(field.rstrip('_id'))

        # Validate only fields we touched
        try:
            instance.full_clean(exclude=[f for f in concrete if f not in touched])
        except ValidationError as exc:
            raise  # bubble up or wrap as needed

        if instance.pk is None:
            instance.save()
            created = True
        else:
            instance.save(update_fields=touched)
            created = False

        return instance, created
