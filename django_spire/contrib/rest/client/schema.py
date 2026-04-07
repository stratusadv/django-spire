from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TypeVar, Generic, get_args, get_origin

from pydantic import BaseModel

from django_spire.contrib.rest.queryset import RestQuerySet
from django_spire.contrib.rest.client.http import BaseRestHttpClient


TSchema = TypeVar('TSchema', bound=BaseModel)


class RestClientObjectsDescriptor(Generic[TSchema]):
    def __get__(self, obj, objtype=None) -> RestQuerySet[TSchema]:
        if obj is None:
            # Accessed on class - need to create a temporary instance
            obj = objtype()
        return RestQuerySet[TSchema](client=obj, schema_class=obj.schema_class)


class RestSchemaClient(Generic[TSchema], BaseRestHttpClient, ABC):
    schema_class: type[TSchema]
    objects = RestClientObjectsDescriptor[TSchema]()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Extract rest_model_class from generic type parameter if not explicitly set
        if not hasattr(cls, 'rest_model_class') or cls.schema_class is None:
            for base in cls.__orig_bases__:
                origin = get_origin(base)
                if origin is not None and issubclass(origin, RestSchemaClient):
                    args = get_args(base)
                    if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                        cls.schema_class = args[0]
                        break

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_url={self.base_url!r})"

    @abstractmethod
    def fetch_one(self, *args, **kwargs) -> TSchema:
        """
        Override this in subclasses to define how a single object should be fetched
        from the API and parsed into the schema class. By default tries to request the
        base_path using the given params as querystring params and parses the response
        JSON directly into the schema class.

        Returns:
            Parsed Pydantic model instance
        """
        raise NotImplementedError()

    @abstractmethod
    def fetch_many(self, *args, **kwargs) -> list[TSchema]:
        """
        Override this in subclasses to define how a list of schema objects should be
        fetched from the API and parsed into the schema class. By default tries to parse
        request the base_path using the given params as querystring params and parses
        the response JSON directly into a list of schema class instances.

        Returns:
            List of parsed Pydantic model instances
        """
        raise NotImplementedError()
