from __future__ import annotations

import os
import random

from typing import TYPE_CHECKING

from django.core.validators import MinValueValidator, MaxValueValidator
from faker import Faker

if TYPE_CHECKING:
    from typing_extensions import Any

    from django.db import models


class DjangoFieldToFakerData:
    def __init__(
        self,
        model_field: models.Field,
        faker_method: tuple | None = None
    ):
        if isinstance(faker_method, str):
            faker_method = (faker_method,)

        self.model_field = model_field
        self.faker_method = faker_method
        self.faker = Faker()

    @property
    def field_converters(self):
        return {
            'CharField': self._char_field_data,
            'TextField': self._char_field_data,
            'IntegerField': self._integer_field_data,
            'SmallIntegerField': self._integer_field_data,
            'PositiveIntegerField': self._positive_integer_field_data,
            'DecimalField': self._decimal_field_data,
            'DateField': self._date_field_data,
            'DateTimeField': self._date_time_field_data,
            'BooleanField': self._boolean_field_data,
            'EmailField': self._email_field_data,
            'URLField': self._url_field_data,
            'SlugField': self._slug_field_data,
            'UUIDField': self._uuid_field_data,
            'TimeField': self._time_field_data,
            'BinaryField': self._binary_field_data,
        }

    def convert(self):
        if self.faker_method:
            result = self._use_faker_with_method()

            if result is not None:
                return result

        converter = self.field_converters.get(self.model_field.get_internal_type())

        if converter is None:
            message = f'No handler for {self.model_field.get_internal_type()}'
            raise Exception(message)

        return converter()

    def _get_min_max_from_validators(self):
        min_value = 0
        max_value = 10000

        for validator in self.model_field.validators:
            if isinstance(validator, MinValueValidator):
                min_value = validator.limit_value
            elif isinstance(validator, MaxValueValidator):
                max_value = validator.limit_value

        return min_value, max_value

    def _use_faker_with_method(self):
        if isinstance(self.faker_method, tuple):
            method_name = self.faker_method[0]
            kwargs = self.faker_method[1] if len(self.faker_method) > 1 and isinstance(self.faker_method[1], dict) else {}

            method = getattr(self.faker, method_name, None)

            if callable(method):
                return method(**kwargs)

        return None

    def _char_field_data(self):
        max_length = getattr(self.model_field, 'max_length', 255)

        if max_length is None:
            max_length = 255

        if self.model_field.choices:
            choices = [choice[0] for choice in self.model_field.choices]
            return self.faker.random_element(elements=choices)

        return self.faker.text(max_nb_chars=max_length)

    def _integer_field_data(self):
        min_value, max_value = self._get_min_max_from_validators()
        return random.randint(min_value, max_value)

    def _positive_integer_field_data(self):
        _, max_value = self._get_min_max_from_validators()
        return random.randint(0, max_value)

    def _decimal_field_data(self):
        max_digits = getattr(self.model_field, 'max_digits', 5)
        decimal_places = getattr(self.model_field, 'decimal_places', 2)
        max_value = 10 ** (max_digits - decimal_places) - 1
        value = random.uniform(0, max_value)
        return round(value, decimal_places)

    def _date_field_data(self):
        return self.faker.date_between(start_date='-5y', end_date='today')

    def _date_time_field_data(self):
        return self.faker.date_time_between(start_date='-5y', end_date='now')

    def _boolean_field_data(self):
        return random.choice([True, False])

    def _email_field_data(self):
        return self.faker.email()

    def _url_field_data(self):
        return self.faker.url()

    def _slug_field_data(self):
        return self.faker.slug()

    def _uuid_field_data(self):
        return self.faker.uuid4()

    def _time_field_data(self):
        return self.faker.time()

    def _binary_field_data(self):
        return os.urandom(16)


def fake_model_field_value(
    model_class: type[models.Model],
    field_name: str,
    faker_method: str | tuple | None = None
) -> Any:
    field = model_class._meta.get_field(field_name)
    return DjangoFieldToFakerData(field, faker_method).convert()
