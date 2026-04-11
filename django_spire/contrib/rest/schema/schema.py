from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, ClassVar, Self, Generic, TypeVar, overload

from pydantic import BaseModel

if TYPE_CHECKING:
    from django_spire.contrib.rest.schema.schemaset import RestSchemaSet

TSchema = TypeVar('TSchema', bound='RestSchema')


class RestSchemaSetDescriptor(Generic[TSchema]):
    @overload
    def __get__(self, obj: None, owner: type[TSchema]) -> RestSchemaSet[TSchema]: ...

    @overload
    def __get__(self, obj: TSchema, owner: type[TSchema]) -> RestSchemaSet[TSchema]: ...

    def __get__(self, obj, owner: type[TSchema]) -> RestSchemaSet[TSchema]:
        from django_spire.contrib.rest.schema.schemaset import RestSchemaSet
        return RestSchemaSet(schema_class=owner)


class RestSchema(ABC, BaseModel):
    """
    Base class for REST API schemas that should map to django models. with Django-like .objects API.

    Provides interface for interacting with external data sources and for translating to
    and from django model objects.
    """

    # Using a descriptor instead of classproperty for this attribute because it needs to
    # be constructed in a function scope, but we still want precise type hinting to flow
    # through properly - classproperty doesn't achieve this
    objects: ClassVar[RestSchemaSetDescriptor[Self]] = RestSchemaSetDescriptor[Self]()

    @classmethod
    def read_one(cls, **request_params) -> Self:
        raise NotImplementedError()

    @classmethod
    def read_many(cls, **request_params) -> list[Self]:
        raise NotImplementedError()
