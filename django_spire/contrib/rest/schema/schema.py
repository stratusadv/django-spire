from __future__ import annotations

from abc import ABC
from inspect import isabstract
from typing import TYPE_CHECKING, ClassVar, Self

from pydantic import BaseModel

if TYPE_CHECKING:
    from django_spire.contrib.rest.schema.schemaset import RestSchemaSet


class RestSchema(ABC, BaseModel):
    """
    Base class for REST API schemas that should map to django models with Django-like .objects API.

    Provides a Django QuerySet - like interface for interacting with external REST-based data sources.

    Subclasses need to assign an instance of a RestSchemaSet subclass to the objects class:
        objects = MySchemaSet
    """

    objects: ClassVar[RestSchemaSet[Self]]

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)

        if not isabstract(cls):
            from django_spire.contrib.rest.schema.schemaset import RestSchemaSet
            objects = getattr(cls, 'objects', None)

            if not isinstance(objects, RestSchemaSet):
                message = f'{cls.__name__}.objects must be an instance of a RestSchemaSet subclass.'
                raise TypeError(message)

            cls.objects = objects.__class__(schema_class=cls)