from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, ClassVar, Self

from pydantic import BaseModel

if TYPE_CHECKING:
    from django_spire.contrib.rest.schema.schemaset import RestSchemaSet


class RestSchema(ABC, BaseModel):
    """
    Base class for REST API schemas that should map to django models with Django-like .objects API.

    Provides an interface for interacting with external data sources and for translating to
    and from django model objects.

    Subclasses need to assign an instance of a RestSchemaSet subclass to the objects class attr:
        objects = MySchemaSet
    """

    objects: ClassVar[RestSchemaSet[Self]]

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        from django_spire.contrib.rest.schema.schemaset import RestSchemaSet

        super().__pydantic_init_subclass__(**kwargs)

        obj = getattr(cls, 'objects', None)

        if obj is not None and isinstance(obj, RestSchemaSet):
            cls.objects = obj.__class__(schema_class=cls)
        else:
            raise ValueError(f'Invalid value assigned to objects class attribute for RestSchema subclass {cls.__name__} - must be an instance of a RestSchemaSet subclass.')
