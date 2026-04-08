from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar, TYPE_CHECKING, get_origin, get_args

from django.db.models import Model
from pydantic import BaseModel

from django_spire.contrib.constructor import BaseDjangoModelConstructor

if TYPE_CHECKING:
    from django_spire.contrib.rest import RestSchema
    from django_spire.contrib.rest.queryset import RestSchemaSet


TModel = TypeVar('TModel', bound=Model)
TSchema = TypeVar('TSchema', bound='RestSchema')


class BaseRestService(BaseDjangoModelConstructor[TModel], ABC, Generic[TModel, TSchema]):
    """
    Base service for REST API integration with Django models.

    Usage:
        class UserRestService(BaseRestService['User', UserSchema]):
            field_mapping = {'first_name': 'firstName'}

        # Schema class is auto-extracted from generic parameter
        service = UserRestService(obj=user)
        users = service.objects.all()
    """
    obj: TModel
    _schema_class: type[TSchema] | None = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Extract schema class from generic type parameters
        # BaseRestService[TModel, TSchema] -> extract TSchema (second param)
        for base in getattr(cls, '__orig_bases__', []):
            origin = get_origin(base)
            if origin is not None and issubclass(origin, BaseRestService):
                args = get_args(base)
                if len(args) >= 2:
                    schema_arg = args[1]
                    if isinstance(schema_arg, type) and issubclass(schema_arg, BaseModel):
                        cls._schema_class = schema_arg
                        break

        # Validate: must have schema_class
        if ABC not in cls.__bases__:
            if getattr(cls, '_schema_class', None) is None:
                raise TypeError(
                    f"{cls.__name__} must specify schema type parameter. "
                    f"Example: class {cls.__name__}(BaseRestService[MyModel, MySchema])"
                )

    @property
    def schema_class(self) -> type[TSchema]:
        """Get the schema class from generic parameter."""
        if self._schema_class is not None:
            return self._schema_class
        raise ValueError("No schema class configured")

    @property
    def objects(self) -> RestSchemaSet[TSchema]:
        """Access RestQuerySet for fetching data from the API."""
        return self.schema_class.objects

    def model_to_schema(self, model: TModel) -> TSchema:
        """Convert Django model to REST schema."""
        data = {}
        schema_class = self.schema_class
        schema_fields = schema_class.model_fields.keys()

        for schema_field in schema_fields:
            reverse_mapping = {v: k for k, v in self.field_mapping.items()}
            model_field = reverse_mapping.get(schema_field, schema_field)

            if hasattr(model, model_field):
                value = getattr(model, model_field)
                data[schema_field] = value

        return schema_class(**data)

    def to_schema(self) -> TSchema:
        """Convert bound model to schema."""
        return self.model_to_schema(self.obj)

    def schema_to_model(self, schema: TSchema, model: TModel | None = None) -> TModel:
        """Convert REST schema to Django model."""
        if model is None:
            model = self.obj.__class__()

        schema_dict = schema.model_dump()

        for schema_field, value in schema_dict.items():
            reverse_mapping = {v: k for k, v in self.field_mapping.items()}
            model_field = reverse_mapping.get(schema_field, schema_field)

            if hasattr(model, model_field):
                setattr(model, model_field, value)

        return model

    def get_identifier(self, model: TModel) -> str:
        """Get API identifier for model (default: pk)."""
        return str(model.pk)
