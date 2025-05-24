from __future__ import annotations
from typing import Any

from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.db.models import Model


class InvalidFieldError(FieldDoesNotExist):
    """Raised when a kwarg does not match a concrete updatable model field."""


@transaction.atomic
def update_model_fields(instance: Model, **data: Any) -> Model:
    """
    Apply keyword data to a model instance and persist it.
    - Raises InvalidFieldError if a kwarg does not correspond to a concrete
      (non-m2m, non-reverse) field on the model.
    """
    if not data:
        return instance

    concrete_fields = {
        f.name for f in instance._meta.get_fields()
        if f.concrete and not f.many_to_many and not f.one_to_many
    }

    # Allow *_id shortcut for FKs if desired
    fk_id_aliases = {
        f"{f.name}_id" for f in instance._meta.get_fields() if f.many_to_one
    }
    allowed_fields = concrete_fields | fk_id_aliases

    for field, value in data.items():

        if field not in allowed_fields:
            raise InvalidFieldError(
                f"'{field}' is not a valid updatable field on "
                f"model '{instance.__class__.__name__}'"
            )

        setattr(instance, field, value)

    instance.full_clean(exclude=[f for f in concrete_fields if f not in data])
    instance.save(
        update_fields=[f for f in data.keys() if not f.endswith("_id")]
    )
    return instance
