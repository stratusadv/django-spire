from __future__ import annotations

import logging

from abc import ABC
from itertools import chain
from typing import Generic, TypeVar

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import transaction
from django.db.models import Model, Field, AutoField, ForeignObjectRel, FileField

from django_spire.contrib.constructor.django_model_constructor import BaseDjangoModelConstructor
from django_spire.contrib.service.exceptions import ServiceError



log = logging.getLogger(__name__)

TypeDjangoModel_co = TypeVar('TypeDjangoModel_co', bound=Model, covariant=True)


class BaseDjangoModelService(
    BaseDjangoModelConstructor[TypeDjangoModel_co],
    ABC,
    Generic[TypeDjangoModel_co]
):
    def _set_non_m2m_fields(self, **field_data: dict):
        model_fields = self.obj._meta.fields

        file_field_list = []
        updated_fields = []

        for field in model_fields:
            if isinstance(field, AutoField) or field.name not in field_data:
                continue

            # Defer saving file-type fields until after the other fields, so a
            # callable upload_to can use the values from other fields (from django's construct_instance).
            if isinstance(field, FileField):
                file_field_list.append(field)
                updated_fields.append(field.name)
            else:
                field.save_form_data(self.obj, field_data[field.name])
                updated_fields.append(field.name)

        # Update foreign key id aliases in field_data for
        # related fields that weren't already updated above
        foreign_key_id_aliases = [
            f"{field.name}_id" for field in model_fields
            if f"{field.name}_id" in field_data and field.many_to_one and field.name not in updated_fields
        ]

        for field_name in foreign_key_id_aliases:
            setattr(self.obj, field_name, field_data[field_name])

        # Update file fields deferred from earlier
        for field in file_field_list:
            field.save_form_data(self.obj, field_data[field.name])

    def _set_m2m_fields(self, **field_data):
        model_meta = self.obj._meta

        for field in chain(model_meta.many_to_many, model_meta.private_fields):
            if not hasattr(field, "save_form_data"):
                continue
            if field.name in field_data:
                field.save_form_data(self.obj, field_data[field.name])

    @transaction.atomic
    def save_model_obj(self, **field_data: dict | None) -> tuple[Model, bool]:
        """
        This is the core service method for saving a Django model object with field data provided via kwargs.
        It will update the object with the given kwargs and handle any upstream attribute changes that were applied
        directly to the model instance (i.e. it can also be called without any kwargs, similar to `Model.save()`).

        Its purpose is to run extra operations related to the model instance that need to run each time
        the model is saved - it is meant to replace the need for overriding `BaseModelForm.save()` or `Model.save()`.

        It is designed to emulate django's `BaseModelForm.save()` method as close as possible:
        first, in `_set_non_m2m_fields`, it updates the fields on `self.obj` using logic similar to `django.forms.models.construct_instance`,
        then it calls self.obj.save(), then updates the m2m fields on the object instance
        using logic similar to django's `BaseModelForm._save_m2m()` method. In all cases,
        it treats the incoming `field_data` exactly the same as `cleaned_data` is treated
        in the django code that it is emulating, and therefore does not perform any validation 
        on the data as it is assumed that field_data has already been validated upstream.

        Args:
            **field_data:

        Returns:
            tuple[Model, bool]

        """

        new_model_obj_was_created = True if self.model_obj_is_new else False

        self._set_non_m2m_fields(**field_data)
        self.obj.save()
        self._set_m2m_fields(**field_data)

        return self.obj, new_model_obj_was_created
