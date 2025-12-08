from __future__ import annotations

import datetime

from unittest import TestCase
from uuid import UUID

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django_spire.core.converters.to_data import DjangoFieldToFakerData, fake_model_field_value


class TestDjangoFieldToFakerData(TestCase):
    def test_binary_field_data(self) -> None:
        class Model(models.Model):
            data = models.BinaryField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('data')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, bytes)
        assert len(result) == 16

    def test_boolean_field_data(self) -> None:
        class Model(models.Model):
            is_active = models.BooleanField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('is_active')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, bool)

    def test_char_field_data(self) -> None:
        class Model(models.Model):
            name = models.CharField(max_length=50)

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('name')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, str)
        assert len(result) <= 50

    def test_char_field_with_choices(self) -> None:
        class Model(models.Model):
            status = models.CharField(
                max_length=10,
                choices=[('A', 'Active'), ('I', 'Inactive')]
            )

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('status')
        result = DjangoFieldToFakerData(field).convert()

        assert result in ['A', 'I']

    def test_custom_faker_method(self) -> None:
        class Model(models.Model):
            name = models.CharField(max_length=100)

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('name')
        result = DjangoFieldToFakerData(field, faker_method=('first_name',)).convert()

        assert isinstance(result, str)

    def test_custom_faker_method_with_kwargs(self) -> None:
        class Model(models.Model):
            number = models.IntegerField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('number')
        result = DjangoFieldToFakerData(
            field,
            faker_method=('random_int', {'min': 100, 'max': 200})
        ).convert()

        assert isinstance(result, int)
        assert 100 <= result <= 200

    def test_date_field_data(self) -> None:
        class Model(models.Model):
            created = models.DateField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('created')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, datetime.date)

    def test_date_time_field_data(self) -> None:
        class Model(models.Model):
            created_at = models.DateTimeField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('created_at')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, datetime.datetime)

    def test_decimal_field_data(self) -> None:
        class Model(models.Model):
            price = models.DecimalField(max_digits=10, decimal_places=2)

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('price')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, float)

    def test_email_field_data(self) -> None:
        """EmailField.get_internal_type() returns 'CharField', so it uses _char_field_data"""

        class Model(models.Model):
            email = models.EmailField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('email')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, str)

    def test_integer_field_data(self) -> None:
        class Model(models.Model):
            count = models.IntegerField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('count')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, int)

    def test_integer_field_with_validators(self) -> None:
        class Model(models.Model):
            count = models.IntegerField(
                validators=[MinValueValidator(10), MaxValueValidator(20)]
            )

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('count')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, int)
        assert 10 <= result <= 20

    def test_positive_integer_field_data(self) -> None:
        class Model(models.Model):
            count = models.PositiveIntegerField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('count')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, int)
        assert result >= 0

    def test_slug_field_data(self) -> None:
        class Model(models.Model):
            slug = models.SlugField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('slug')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, str)

    def test_text_field_data(self) -> None:
        class Model(models.Model):
            description = models.TextField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('description')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, str)

    def test_time_field_data(self) -> None:
        class Model(models.Model):
            start_time = models.TimeField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('start_time')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, str)

    def test_url_field_data(self) -> None:
        """URLField.get_internal_type() returns 'CharField', so it uses _char_field_data"""

        class Model(models.Model):
            website = models.URLField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('website')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, str)

    def test_uuid_field_data(self) -> None:
        class Model(models.Model):
            uuid = models.UUIDField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model._meta.get_field('uuid')
        result = DjangoFieldToFakerData(field).convert()

        assert isinstance(result, str)
        UUID(result)


class TestFakeModelFieldValue(TestCase):
    def test_fake_model_field_value(self) -> None:
        class Model(models.Model):
            name = models.CharField(max_length=50)

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        result = fake_model_field_value(Model, 'name')

        assert isinstance(result, str)
        assert len(result) <= 50

    def test_fake_model_field_value_with_faker_method(self) -> None:
        class Model(models.Model):
            email = models.EmailField()

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        result = fake_model_field_value(Model, 'email', faker_method=('email',))

        assert isinstance(result, str)
        assert '@' in result
