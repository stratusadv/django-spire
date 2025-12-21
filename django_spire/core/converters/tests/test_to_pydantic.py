from __future__ import annotations

import enum

from typing import get_args, get_origin, Union
from unittest import TestCase

from pydantic import BaseModel

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from django_spire.core.converters.to_pydantic import DjangoToPydanticFieldConverter, django_to_pydantic_model


def is_optional(t: type) -> bool:
    return get_origin(t) is Union and type(None) in get_args(t)


class TestDjangoModelToPydanticModel(TestCase):
    def test_comprehensive_model_conversion(self) -> None:
        class ComprehensiveModel(models.Model):
            char_field_with_choices = models.CharField(
                max_length=10,
                choices=[('A', 'Active'), ('I', 'Inactive')],
                default='A',
                help_text='Status of the item',
                unique=True,
                null=False
            )
            char_field_no_choices = models.CharField(
                max_length=20,
                default='default',
                help_text='Description',
                unique=False,
                null=True
            )
            int_field = models.IntegerField(
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                default=50,
                help_text='Count',
                unique=False,
                null=True
            )
            decimal_field = models.DecimalField(
                max_digits=5,
                decimal_places=2,
                default=0.0,
                help_text='Price',
                unique=False,
                null=False
            )
            boolean_field = models.BooleanField(
                default=True,
                help_text='Active',
                null=False
            )

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        PydanticModel = django_to_pydantic_model(ComprehensiveModel)
        assert PydanticModel.__name__ == 'ComprehensiveModel'

    def test_conversion_with_custom_base_class(self) -> None:
        class CustomBase(BaseModel):
            extra_field: str = 'extra'

        class CustomModel(models.Model):
            char_field = models.CharField(max_length=10, default='custom')

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        PydanticModel = django_to_pydantic_model(CustomModel, base_class=CustomBase)
        instance = PydanticModel(id=1, char_field='custom', extra_field='extra')

        assert instance.char_field == 'custom'
        assert instance.extra_field == 'extra'

    def test_exclude_fields(self) -> None:
        class SimpleModel2(models.Model):
            field1 = models.CharField(max_length=50, default='value1')
            field2 = models.IntegerField(default=10)
            field3 = models.BooleanField(default=True)

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        PydanticModel = django_to_pydantic_model(SimpleModel2, exclude_fields=['field2'])
        fields = PydanticModel.model_fields
        assert 'id' in fields
        assert 'field1' in fields
        assert 'field3' in fields
        assert 'field2' not in fields

    def test_include_and_exclude(self) -> None:
        class SimpleModel3(models.Model):
            field1 = models.CharField(max_length=50, default='value1')
            field2 = models.IntegerField(default=10)
            field3 = models.BooleanField(default=True)
            field4 = models.CharField(max_length=100, default='value4')

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        PydanticModel = django_to_pydantic_model(
            SimpleModel3,
            include_fields=['id', 'field1', 'field2', 'field3'],
            exclude_fields=['field2']
        )

        fields = PydanticModel.model_fields
        assert 'id' in fields
        assert 'field1' in fields
        assert 'field3' in fields
        assert 'field2' not in fields
        assert 'field4' not in fields

    def test_include_fields_only(self) -> None:
        class SimpleModel1(models.Model):
            field1 = models.CharField(max_length=50, default='value1')
            field2 = models.IntegerField(default=10)
            field3 = models.BooleanField(default=True)

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        PydanticModel = django_to_pydantic_model(SimpleModel1, include_fields=['id', 'field1', 'field3'])
        fields = PydanticModel.model_fields
        assert 'id' in fields
        assert 'field1' in fields
        assert 'field3' in fields
        assert 'field2' not in fields


class TestDjangoToPydanticFieldConverter(TestCase):
    # def test_nullable_field_is_optional(self):
    #     class Model(models.Model):
    #         char_field = models.CharField(max_length=10, null=True)

    #         class Meta:
    #             managed = False

    #         def __str__(self) -> str:
    #             return 'model'

    #     field = Model._meta.get_field('char_field')
    #     field_type, _ = DjangoToPydanticFieldConverter(field).build_field()

    #     assert is_optional(field_type)

    def test_charfield_constraints_applied(self) -> None:
        class Model4(models.Model):
            name = models.CharField(max_length=30)

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model4._meta.get_field('name')
        field_type, _ = DjangoToPydanticFieldConverter(field).build_field()

        assert 'max_length=30' in str(field_type)

    def test_decimalfield_constraints_applied(self) -> None:
        class Model6(models.Model):
            amount = models.DecimalField(max_digits=5, decimal_places=2)

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model6._meta.get_field('amount')
        field_type, _ = DjangoToPydanticFieldConverter(field).build_field()

        assert 'max_digits=5' in str(field_type)
        assert 'decimal_places=2' in str(field_type)

    def test_enum_created_for_choices(self) -> None:
        class Model3(models.Model):
            status = models.CharField(
                max_length=10,
                choices=[('A', 'Active'), ('I', 'Inactive')],
                default='A'
            )

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model3._meta.get_field('status')
        field_type, _ = DjangoToPydanticFieldConverter(field).build_field()

        assert issubclass(field_type, enum.Enum)
        assert set(field_type.__members__) == {'A', 'I'}

    def test_field_with_no_default_sets_none(self) -> None:
        class Model1(models.Model):
            char_field = models.CharField(max_length=10, null=True)

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model1._meta.get_field('char_field')
        _, field_info = DjangoToPydanticFieldConverter(field).build_field()

        assert field_info.default is None

    def test_help_text_becomes_description(self) -> None:
        class Model2(models.Model):
            char_field = models.CharField(max_length=10, help_text='hello')

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model2._meta.get_field('char_field')
        _, field_info = DjangoToPydanticFieldConverter(field).build_field()

        assert field_info.description == 'hello'

    def test_integerfield_validators_become_constraints(self) -> None:
        # TODO(Nathan): test needs to be corrected.

        class Model5(models.Model):
            count = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

            class Meta:
                managed = False

            def __str__(self) -> str:
                return 'model'

        field = Model5._meta.get_field('count')
        field_type, _ = DjangoToPydanticFieldConverter(field).build_field()
        assert 'int' in str(field_type)
