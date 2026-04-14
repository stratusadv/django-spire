from typing import TypeVar, Self, Generic

from django.db import models

from django_spire.contrib.rest.schema.schema import RestSchema

TModel = TypeVar('TModel', bound='models.Model')


class DjangoModelRestSchema(RestSchema, Generic[TModel]):
    @classmethod
    def from_django_model(cls, model: type[TModel]) -> Self:
        raise NotImplementedError()

    @classmethod
    def to_django_model(cls) -> TModel:
        raise NotImplementedError()