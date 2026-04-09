from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self, Generic, TypeVar, overload

from pydantic import BaseModel

from django_spire.contrib.rest.client.http import BaseRestHttpClient
from django_spire.contrib.rest.client.schema import RestSchemaClient

if TYPE_CHECKING:
    from django_spire.contrib.rest.schemaset import RestSchemaSet

TSchema = TypeVar('TSchema', bound='RestSchema')
TModel = TypeVar('TModel', bound='BaseModel')


class RestSchemaMeta(Generic[TSchema]):
    rest_client: RestSchemaClient[TSchema] | None = None


class RestSchemaSetDescriptor(Generic[TSchema]):
    @overload
    def __get__(self, obj: None, owner: type[TSchema]) -> RestSchemaSet[TSchema]: ...

    @overload
    def __get__(self, obj: TSchema, owner: type[TSchema]) -> RestSchemaSet[TSchema]: ...

    def __get__(self, obj, owner: type[TSchema]) -> RestSchemaSet[TSchema]:
        from django_spire.contrib.rest.schemaset import RestSchemaSet
        return RestSchemaSet(schema_class=owner)


class RestSchema(BaseModel):
    """
    Base class for REST API schemas with Django-like .objects API.

    Combines Pydantic field definitions with REST client functionality.
    """

    # Using a descriptor instead of classproperty for this attribute because it needs to
    # be constructed in a function scope, but we still want precise type hinting to flow
    # through properly - classproperty doesn't achieve this
    objects: ClassVar[RestSchemaSetDescriptor[Self]] = RestSchemaSetDescriptor[Self]()

    rest_client: RestSchemaClient[Self] = None

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        if not isinstance(cls.rest_client, RestSchemaClient) or not issubclass(cls.rest_client.schema_class, cls):
            raise TypeError(f'Invalid rest client configured for schema {cls.__name__}')
        # Build merged meta options
        # cls._meta = cls._build_meta()


    # class Meta(RestSchemaMeta):
    #     pass

    # @classmethod
    # def _build_meta(cls) -> RestSchemaMeta:
    #     meta = RestSchemaMeta()
    #     for klass in reversed(cls.__mro__):
    #         if hasattr(klass, 'Meta') and klass.Meta is not RestSchemaMeta:
    #             for attr in ['base_url', 'base_path', 'results_key', 'id_field', 'timeout', 'headers']:
    #                 if hasattr(klass.Meta, attr):
    #                     setattr(meta, attr, getattr(klass.Meta, attr))
    #     return meta

    @classmethod
    def from_django_model(cls, model: type[TModel]) -> Self:
        raise NotImplementedError()

    def to_django_model(self) -> TModel:
        raise NotImplementedError()