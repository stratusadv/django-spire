from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Self, Generic, TypeVar, overload

from django.db.models import Manager
from pydantic import BaseModel

from django_spire.contrib.rest.client.http import BaseRestHttpClient

if TYPE_CHECKING:
    from django_spire.contrib.rest.schemaset import RestSchemaSet

TSchema = TypeVar('TSchema', bound='RestSchema')
TModel = TypeVar('TModel', bound='BaseModel')


class RestSchemaMeta:
    base_url: str = ''
    base_path: str = ''
    results_key: str | None = None
    id_field: str = 'id'
    timeout: int = 30
    headers: dict[str, str] = {}


class RestSchemaManager(Generic[TSchema]):
    @overload
    def __get__(self, obj: None, owner: type[TSchema]) -> RestSchemaSet[TSchema]: ...

    @overload
    def __get__(self, obj: TSchema, owner: type[TSchema]) -> RestSchemaSet[TSchema]: ...

    def __get__(self, obj, owner: type[TSchema]) -> RestSchemaSet[TSchema]:
        from django_spire.contrib.rest.schemaset import RestSchemaSet
        return RestSchemaSet(schema_class=owner)


class RestSchema(BaseModel, Generic[TModel]):
    """
    Base class for REST API schemas with Django-like .objects API.

    Combines Pydantic field definitions with REST client functionality.
    """
    objects: ClassVar[RestSchemaManager[Self]] = RestSchemaManager()

    class Meta(RestSchemaMeta):
        pass

    @classmethod
    @property
    def rest_client(cls) -> RestClient:
        return cls.objects.rest_client

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        # Build merged meta options
        cls._meta = cls._build_meta()

    @classmethod
    def _build_meta(cls) -> RestSchemaMeta:
        meta = RestSchemaMeta()
        for klass in reversed(cls.__mro__):
            if hasattr(klass, 'Meta') and klass.Meta is not RestSchemaMeta:
                for attr in ['base_url', 'base_path', 'results_key', 'id_field', 'timeout', 'headers']:
                    if hasattr(klass.Meta, attr):
                        setattr(meta, attr, getattr(klass.Meta, attr))
        return meta

    @classmethod
    def _get_http_client(cls) -> BaseRestHttpClient:
        if not hasattr(cls, '_http_client'):
            meta = cls._meta

            class SchemaHttpClient(BaseRestHttpClient):
                base_url = meta.base_url
                base_path = meta.base_path
                timeout = meta.timeout
                base_headers = meta.headers or {}

            cls._http_client = SchemaHttpClient()
        return cls._http_client

    @classmethod
    def fetch_one(cls, identifier: str | int, **params) -> Self:
        """
        Fetch a single object by ID.

        Override for custom behavior.

        Args:
            identifier: The ID of the object to fetch
            **params: Additional query parameters

        Returns:
            A single schema instance
        """
        client = cls._get_http_client()
        response = client.get(path=str(identifier), params=params)
        data = response.json()
        parsed = cls.parse_one_response(data)
        return cls(**parsed)

    @classmethod
    def fetch_many(cls, **params) -> list[Self]:
        """
        Fetch multiple objects.

        Override for custom behavior.

        Args:
            **params: Query parameters (limit, offset, filters, etc.)

        Returns:
            A list of schema instances
        """
        client = cls._get_http_client()
        response = client.get(params=params)
        data = response.json()
        items = cls.parse_list_response(data)
        return [cls(**item) for item in items]

    @classmethod
    def parse_one_response(cls, data: dict) -> dict:
        """
        Parse single object response.

        Override for custom extraction logic.

        Args:
            data: The raw JSON response

        Returns:
            Dictionary of field values for the schema
        """
        return data

    @classmethod
    def parse_list_response(cls, data: dict | list) -> list[dict]:
        """
        Parse list response.

        Override for complex extraction logic.

        Args:
            data: The raw JSON response (list or wrapper object)

        Returns:
            List of dictionaries, one per object
        """
        if isinstance(data, list):
            return data
        if cls._meta.results_key and cls._meta.results_key in data:
            return data[cls._meta.results_key]
        return data

    @classmethod
    def from_django_model(cls, model: type[TModel]) -> Self:
        raise NotImplementedError()

    def to_django_model(self) -> TModel:
        raise NotImplementedError()