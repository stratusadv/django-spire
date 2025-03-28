from math import pi
from typing import Type

from pydantic import Field
from pydantic import create_model

from django.db.models.base import Model
from django.db.models import Field as DjangoField
from django_spire.core.maps import MODEL_FIELD_TYPE_TO_TYPE_MAP


def django_model_to_pydantic_model(
        model_class: Type[Model],
        base_class: Type | None = None
):
    pydantic_fields = {}

    for model_field in model_class._meta.fields:
        model_field_type = MODEL_FIELD_TYPE_TO_TYPE_MAP[model_field.get_internal_type()]

        if model_field.null:
            model_field_type = model_field_type | None

        pydantic_fields[model_field.attname] = (
            model_field_type,
            django_field_to_pydantic_field(model_field)
        )
    return create_model(
            f'{model_class.__name__}',
            __base__=base_class,
            **pydantic_fields
        )


def django_field_to_pydantic_field(field: DjangoField) -> Field:
    kwargs = {
        'description': '',
    }

    if field.null:
        kwargs['default'] = None

    if field.get_internal_type() in ['DateField']:
        kwargs['description'] += 'Date Format: YYYY-MM-DD '
        kwargs['examples'] = ['2022-01-01']

    if field.get_internal_type() in ['DateTimeField']:
        kwargs['description'] += 'Date Format: YYYY-MM-DD HH:MM:SS '
        kwargs['examples'] = ['2022-01-01 13:37:00']

    if field.unique:
        kwargs['description'] += 'Is Unique: True '

    if field.get_internal_type() in ['CharField', 'TextField'] and field.max_length:
        kwargs['max_length'] = int(field.max_length)

    if field.get_internal_type() in ['DecimalField']:
        whole_number_length = field.max_digits - field.decimal_places
        decimal_places_length = field.decimal_places
        max_value = float('9' * whole_number_length + "." + '9' * field.decimal_places)
        min_value = -max_value
        # Using Pi as example values. Multiplied by formulas
        kwargs['examples'] = f"{pi * (10 ** (whole_number_length - 1)):{whole_number_length}.{decimal_places_length}f}"
        kwargs['lt'] = max_value
        kwargs['gt'] = min_value
        """
        experimental:
        kwargs['description'] += 'Decimal Field Format: {}.{}'.format(
            'X' * whole_number_length,
            'X' * field.decimal_places)
        """
        # Below line did not work. Only made the increments of value by 0.01
        # kwargs['multipleOf'] = 10 ** (-decimal_places_length)
    return Field(**kwargs)
