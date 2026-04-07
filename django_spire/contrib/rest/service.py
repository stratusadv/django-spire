from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar

from django.db.models import Model
from pydantic import BaseModel

from django_spire.contrib.constructor import BaseDjangoModelConstructor
from django_spire.contrib.constructor.constructor import BaseConstructor
from django_spire.contrib.rest.client.schema import RestSchemaClient


TModel = TypeVar('TModel', bound=Model)
TSchema = TypeVar('TSchema', bound=BaseModel)
TClient = TypeVar('TClient', bound=RestSchemaClient)


class BaseRestService(BaseDjangoModelConstructor[TModel], ABC, Generic[TModel, TSchema, TClient]):
    obj: TModel
    client: TClient | None = None
    field_mapping: dict[str, str] = {}  # model_field -> schema_field

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Only validate concrete classes (not ABC subclasses)
        if ABC not in cls.__bases__:
            if cls.client is None:
                raise TypeError(
                    f"{cls.__name__} must define a 'client' class attribute. "
                    f"Example: client = MyClient()"
                )

    def model_to_schema(self, model: TModel) -> TSchema:
        data = {}

        # Get all schema field names
        schema_class = self.client.schema_class
        schema_fields = schema_class.model_fields.keys()

        for schema_field in schema_fields:
            # Check if there's a reverse mapping for this field (schema -> model)
            reverse_mapping = {v: k for k, v in self.field_mapping.items()}
            model_field = reverse_mapping.get(schema_field, schema_field)

            # Get value from model
            if hasattr(model, model_field):
                value = getattr(model, model_field)
                data[schema_field] = value

        return schema_class(**data)

    def self_obj_to_schema(self) -> TSchema:
        return self.model_to_schema(self.obj)

    def schema_to_model(self, schema: TSchema, model: TModel | None = None) -> TModel:
        if model is None:
            model = self.obj.__class__()

        schema_dict = schema.model_dump()

        for schema_field, value in schema_dict.items():
            # Check if there's a reverse mapping for this field
            reverse_mapping = {v: k for k, v in self.field_mapping.items()}
            model_field = reverse_mapping.get(schema_field, schema_field)

            # Set value on model if the field exists
            if hasattr(model, model_field):
                setattr(model, model_field, value)

        return model

    def get_identifier(self, model: TModel) -> str:
        return str(model.pk)

    def fetch_one(self, *args, **kwargs) -> TSchema:
        return self.client.fetch_one(*args, **kwargs)
