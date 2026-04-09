from __future__ import annotations

from abc import abstractmethod, ABC
from typing import TypeVar, Generic, get_args, get_origin

from pydantic import BaseModel

from django_spire.contrib.rest import RestSchema
from django_spire.contrib.rest.client.http import BaseRestHttpClient


TSchema = TypeVar('TSchema', bound=RestSchema)


class RestSchemaClient(Generic[TSchema], BaseRestHttpClient, ABC):
    schema_class: type[TSchema]

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
    def read(
        self,
        *args,
        **kwargs,
    ) -> list[TSchema]:
        raise NotImplementedError()

    # optional - allows schemasets to fetch single objects directly from the rest api
    def read_one(
        self,
        *args,
        **kwargs,
    ) -> TSchema:
        raise NotImplementedError()
