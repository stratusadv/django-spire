from datetime import date
from math import pi

from django.db.models import Field as DjangoField
from pydantic.fields import Field


class SeedIntelFieldFactory:

    def __init__(self, model_field: DjangoField):
        self.model_field = model_field

    def build_field(self) -> Field:
        kwargs = {
            'description': '',
        }

        if self.model_field.null:
            kwargs['default'] = None

        if self.model_field.get_internal_type() in ['DateField']:
            kwargs['description'] += 'Date Format: YYYY-MM-DD '
            kwargs['examples'] = ['2022-01-01']

        if self.model_field.get_internal_type() in ['DateTimeField']:
            kwargs['description'] += 'Date Format: YYYY-MM-DD HH:MM:SS '
            kwargs['examples'] = ['2022-01-01 13:37:00']

        if self.model_field.unique:
            kwargs['description'] += 'Is Unique: True '

        if self.model_field.get_internal_type() in ['CharField', 'TextField'] and self.model_field.max_length:
            kwargs['max_length'] = int(self.model_field.max_length)

        if self.model_field.get_internal_type() in ['DecimalField']:
            whole_number_length = self.model_field.max_digits - self.model_field.decimal_places
            decimal_places_length = self.model_field.decimal_places
            max_value = float('9' * whole_number_length + "." + '9' * self.model_field.decimal_places)
            min_value = -max_value
            # Using Pi as example values. Multiplied by formulas
            kwargs['examples'] = f"{pi * (10 ** (whole_number_length - 1)):{whole_number_length}.{decimal_places_length}f}"
            kwargs['lt'] = max_value
            kwargs['gt'] = min_value
            """
            experimental:
            kwargs['description'] += 'Decimal Field Format: {}.{}'.format(
                'X' * whole_number_length,
                'X' * self.model_field.decimal_places)
            """
            # Below line did not work. Only made the increments of value by 0.01
            # kwargs['multipleOf'] = 10 ** (-decimal_places_length)
        return Field(**kwargs)
