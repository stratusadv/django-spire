from pydantic import Field, constr, conint, condecimal, create_model
from typing import Tuple, Type, Any, Optional

from django.db import models

from django.core import validators

from django_spire.core.converters.to_enums import django_choices_to_enums
from django_spire.core.maps import MODEL_FIELD_TYPE_TO_TYPE_MAP


def django_to_pydantic_model(
        model_class: Type[models.Model],
        base_class: Type | None = None,
        include: str | list| tuple | None = None,
        exclude: str | list | tuple | None = None
):
    if not issubclass(model_class, models.Model):
        raise ValueError("model_class must be a subclass of django.db.models.Model")

    pydantic_fields = {}

    for model_field in model_class._meta.fields:
        field_name = model_field.attname

        if include is not None and field_name not in include:
            continue

        if exclude is not None and field_name in exclude:
            continue

        converter = DjangoToPydanticFieldConverter(model_field)
        pydantic_fields[field_name] = converter.build_field()

    return create_model(
        f'{model_class.__name__}',
        __base__=base_class,
        **pydantic_fields
    )


class DjangoToPydanticFieldConverter:

    def __init__(self, model_field: models.Field):
        self.model_field = model_field
        self.kwargs = {}

        self._build_metadata()
        self.field_type = self._get_pydantic_type()
        self._wrap_nullable()

    @property
    def field_handlers(self):
        return {
            'CharField': self._build_char_field,
            'IntegerField': self._build_integer_field,
            'SmallIntegerField': self._build_integer_field,
            'DecimalField': self._build_decimal_field,
            'DateField': self._build_date_field,
            'DateTimeField': self._build_date_time_field,
        }

    def _base_type(self):
        return MODEL_FIELD_TYPE_TO_TYPE_MAP.get(
            self.model_field.get_internal_type(),
            str
        )

    def _build_char_field(self) -> Type:
        if self.model_field.max_length:
            return constr(max_length=self.model_field.max_length)
        return str

    def _build_date_field(self) -> Type:
        self.kwargs['example'] = '2022-01-01'
        self.kwargs['json_schema_extra']['example'] = '2022-01-01'
        return self._base_type()

    def _build_date_time_field(self) -> Type:
        self.kwargs['example'] = '2022-01-01 13:37:00'
        self.kwargs['json_schema_extra']['example'] = '2022-01-01 13:37:00'
        return self._base_type()

    def _build_integer_field(self) -> Type:
        ge, le = None, None
        for validator in self.model_field.validators:
            if isinstance(validator, validators.MinValueValidator):
                ge = validator.limit_value
            elif isinstance(validator, validators.MaxValueValidator):
                le = validator.limit_value

        if ge is not None or le is not None:
            return conint(ge=ge, le=le)
        return int

    def _build_decimal_field(self) -> Type:
        self.kwargs['json_schema_extra']['example'] = '0.00'
        self.kwargs['json_schema_extra']['max_digits'] = self.model_field.max_digits
        self.kwargs['json_schema_extra']['decimal_places'] = self.model_field.decimal_places

        return condecimal(
            max_digits=self.model_field.max_digits,
            decimal_places=self.model_field.decimal_places
        )

    def _build_enum_type(self):
        enum_name = f"{self.model_field.name.capitalize()}Enum"
        return django_choices_to_enums(enum_name, self.model_field.choices)

    def build_field(self) -> Tuple[Type, Any]:
        """Build and return the Pydantic field type and Field object."""
        return self.field_type, Field(**self.kwargs)

    def _build_metadata(self):
        if self.model_field.default is not models.NOT_PROVIDED:
            if callable(self.model_field.default):
                self.kwargs['default'] = self.model_field.default()
            else:
                self.kwargs['default'] = self.model_field.default

        if self.model_field.null and self.model_field.default is models.NOT_PROVIDED:
            self.kwargs['default'] = None

        # Todo: Nathan said their is a description field on a django model.
        if self.model_field.help_text:
            self.kwargs['description'] = str(self.model_field.help_text)

        self.kwargs['json_schema_extra'] = {
            'is_unique': self.model_field.unique,
            'is_required': not self.model_field.null,
            'field_name': self.model_field.name
        }

        if self.model_field.choices:
            self.kwargs['json_schema_extra']['choices'] = self.model_field.choices

    def _get_pydantic_type(self) -> Type:
        if self.model_field.choices:
            return self._build_enum_type()

        handler = self.field_handlers.get(self.model_field.get_internal_type())
        if handler:
            return handler()

        return self._base_type()

    def _wrap_nullable(self):
        if self.model_field.null:
            self.field_type = Optional[self.field_type]