from typing import Any

from pydantic import BaseModel

from django_spire.contrib.rest_client.client import RestClient


class BaseRestSchema(ABC, BaseModel):
    def to_dict(self) -> dict:
        return self.model_dump()


class BaseDjangoModelRestSchema(BaseRestSchema):
    @abstractmethod
    def to_django_model_instance(self) -> Model:
        raise NotImplementedError()

    @abstractmethod
    def load_from_django_model_instance(self) -> Model:
        raise NotImplementedError()

