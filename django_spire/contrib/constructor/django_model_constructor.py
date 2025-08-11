from __future__ import annotations

from abc import ABC
from typing import Type, Generic, TypeVar

from django.db.models import Model

from django_spire.contrib.constructor.constructor import BaseConstructor

TypeDjangoModel = TypeVar('TypeDjangoModel', bound=Model, covariant=True)


class BaseDjangoModelConstructor(BaseConstructor[TypeDjangoModel], ABC, Generic[TypeDjangoModel]):
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

    @property
    def obj_class(self) -> Type[TypeDjangoModel]:
        return super().obj_class

    @property
    def _obj_is_valid(self) -> bool:
        return super()._obj_is_valid and isinstance(self.obj, Model) and issubclass(self._obj_type, Model)
