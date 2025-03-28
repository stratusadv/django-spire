from pydantic import Field

from django.db import models
from django.core import validators

from django_spire.core.converters.to_enums import django_choices_to_enums
from django_spire.core.maps import MODEL_FIELD_TYPE_TO_TYPE_MAP


class DjangoFieldToPydanticFieldFactory:

    def __init__(self, model_field: models.Field):
        self.model_field = model_field
        self.field_type = self.get_pydantic_type()
        self.kwargs = {
            'description': model_field.help_text,
            'json_schema_extra': {
                'is_unique': model_field.unique,
                'is_required': not model_field.null
            },
        }

        if self.model_field.default != models.NOT_PROVIDED:
            self.kwargs['default'] = self.model_field.default

        if model_field.choices:
            self.kwargs['json_schema_extra']['choices'] = model_field.choices

        field_type_name = model_field.get_internal_type()
        if field_type_name == 'CharField':
            self._set_char_field()
        elif field_type_name in ['BigIntegerField', 'IntegerField', 'FloatField', 'SmallIntegerField']:
            self._set_number_field()
        elif field_type_name == 'DecimalField':
            self._set_decimal_field()

    def get_pydantic_type(self):
        """Retrieve the corresponding Pydantic type for the Django field."""
        if self.model_field.choices:
            return self.create_enum_for_choices()
        else:
            field_type_name = self.model_field.get_internal_type()
            return MODEL_FIELD_TYPE_TO_TYPE_MAP.get(field_type_name, str)

    def create_enum_for_choices(self):
        enum_name = f"{self.model_field.name.capitalize()}Enum"
        return django_choices_to_enums(enum_name, self.model_field.choices)

    def _add_schema_extra(self, key, value):
        self.kwargs['json_schema_extra'][key] = value

    def _add_kwarg(self, key, value):
        self.kwargs[key] = value

    def _set_char_field(self):
        self._add_kwarg('max_length', self.model_field.max_length)

    def _set_number_field(self):
        for validator in self.model_field.validators:
            if isinstance(validator, validators.MinValueValidator):
                self._add_kwarg('ge', validator.limit_value)
            elif isinstance(validator, validators.MaxValueValidator):
                self._add_kwarg('le', validator.limit_value)

    def _set_decimal_field(self):
        self._add_kwarg('max_digits', self.model_field.max_digits)
        self._add_kwarg('decimal_places', self.model_field.decimal_places)

    def build_field(self):
        """Build and return the Pydantic field tuple."""
        return (self.field_type, Field(**self.kwargs))
