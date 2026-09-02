from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar, Self, Generic

from django_spire.contrib.rest.schema.schema import RestSchema

if TYPE_CHECKING:
    from django.db import models

TModel = TypeVar('TModel', bound='models.Model')


class DjangoModelRestSchema(RestSchema, ABC, Generic[TModel]):
    @classmethod
    @abstractmethod
    def from_django_model(cls, model: type[TModel]) -> Self:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def to_django_model(cls) -> TModel:
        raise NotImplementedError
