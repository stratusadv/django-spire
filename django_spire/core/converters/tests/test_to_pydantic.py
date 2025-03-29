from unittest import TestCase
from typing import get_origin, get_args, Union

from pydantic import BaseModel

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import enum

from django_spire.core.converters.to_pydantic import DjangoToPydanticFieldConverter, django_to_pydantic_model


def is_optional(typ):
    return get_origin(typ) is Union and type(None) in get_args(typ)


class TestDjangoModelToPydanticModel(TestCase):
    def test_comprehensive_model_conversion(self):
        class ComprehensiveModel(models.Model):
            # Django auto-adds an "id" primary key field.
            char_field_with_choices = models.CharField(
                max_length=10,
                choices=[("A", "Active"), ("I", "Inactive")],
                default="A",
                help_text="Status of the item",
                unique=True,
                null=False
            )
            char_field_no_choices = models.CharField(
                max_length=20,
                default="default",
                help_text="Description",
                unique=False,
                null=True
            )
            int_field = models.IntegerField(
                validators=[MinValueValidator(0), MaxValueValidator(100)],
                default=50,
                help_text="Count",
                unique=False,
                null=True
            )
            decimal_field = models.DecimalField(
                max_digits=5,
                decimal_places=2,
                default=0.0,
                help_text="Price",
                unique=False,
                null=False
            )
            boolean_field = models.BooleanField(
                default=True,
                help_text="Active",
                null=False
            )

            class Meta:
                managed = False

        PydanticModel = django_to_pydantic_model(ComprehensiveModel)
        self.assertEqual(PydanticModel.__name__, "ComprehensiveModel")

    def test_conversion_with_custom_base_class(self):
        class CustomBase(BaseModel):
            extra_field: str = "extra"

        class CustomModel(models.Model):
            char_field = models.CharField(max_length=10, default="custom")
            class Meta:
                managed = False

        PydanticModel = django_to_pydantic_model(CustomModel, base_class=CustomBase)
        instance = PydanticModel(id=1)

        self.assertEqual(instance.char_field, "custom")
        self.assertEqual(instance.extra_field, "extra")

    def test_include_fields_only(self):
        class SimpleModel(models.Model):
            field1 = models.CharField(max_length=50, default="value1")
            field2 = models.IntegerField(default=10)
            field3 = models.BooleanField(default=True)
            class Meta:
                managed = False

        PydanticModel = django_to_pydantic_model(SimpleModel, include_fields=["id", "field1", "field3"])
        fields = PydanticModel.__fields__
        self.assertIn("id", fields)
        self.assertIn("field1", fields)
        self.assertIn("field3", fields)
        self.assertNotIn("field2", fields)

    def test_exclude_fields(self):
        class SimpleModel(models.Model):
            field1 = models.CharField(max_length=50, default="value1")
            field2 = models.IntegerField(default=10)
            field3 = models.BooleanField(default=True)
            class Meta:
                managed = False

        PydanticModel = django_to_pydantic_model(SimpleModel, exclude_fields=["field2"])
        fields = PydanticModel.__fields__
        self.assertIn("id", fields)
        self.assertIn("field1", fields)
        self.assertIn("field3", fields)
        self.assertNotIn("field2", fields)

    def test_include_and_exclude(self):
        # Define a simple model with multiple fields.
        class SimpleModel(models.Model):
            field1 = models.CharField(max_length=50, default="value1")
            field2 = models.IntegerField(default=10)
            field3 = models.BooleanField(default=True)
            field4 = models.CharField(max_length=100, default="value4")
            class Meta:
                managed = False

        PydanticModel = django_to_pydantic_model(
            SimpleModel,
            include_fields=["id", "field1", "field2", "field3"],
            exclude_fields=["field2"]
        )
        fields = PydanticModel.__fields__
        self.assertIn("id", fields)
        self.assertIn("field1", fields)
        self.assertIn("field3", fields)
        self.assertNotIn("field2", fields)
        self.assertNotIn("field4", fields)


class TestDjangoToPydanticFieldConverter(TestCase):
    def test_nullable_field_is_optional(self):
        class Model(models.Model):
            char_field = models.CharField(max_length=10, null=True)

            class Meta:
                managed = False

        field = Model._meta.get_field('char_field')
        field_type, _ = DjangoToPydanticFieldConverter(field).build_field()

        self.assertTrue(is_optional(field_type))

    def test_field_with_no_default_sets_none(self):
        class Model(models.Model):
            char_field = models.CharField(max_length=10, null=True)

            class Meta:
                managed = False

        field = Model._meta.get_field('char_field')
        _, field_info = DjangoToPydanticFieldConverter(field).build_field()

        self.assertIsNone(field_info.default)

    def test_field_with_default(self):
        class Model(models.Model):
            char_field = models.CharField(max_length=10, default="abc")

            class Meta:
                managed = False

        field = Model._meta.get_field('char_field')
        _, field_info = DjangoToPydanticFieldConverter(field).build_field()

        self.assertEqual(field_info.default, "abc")

    def test_help_text_becomes_description(self):
        class Model(models.Model):
            char_field = models.CharField(max_length=10, help_text="hello")

            class Meta:
                managed = False

        field = Model._meta.get_field('char_field')
        _, field_info = DjangoToPydanticFieldConverter(field).build_field()

        self.assertEqual(field_info.description, "hello")

    def test_enum_created_for_choices(self):
        class Model(models.Model):
            status = models.CharField(
                max_length=10,
                choices=[("A", "Active"), ("I", "Inactive")],
                default="A"
            )

            class Meta:
                managed = False

        field = Model._meta.get_field('status')
        field_type, _ = DjangoToPydanticFieldConverter(field).build_field()

        self.assertTrue(issubclass(field_type, enum.Enum))
        self.assertEqual(set(field_type.__members__), {"A", "I"})

    def test_charfield_constraints_applied(self):
        class Model(models.Model):
            name = models.CharField(max_length=30)

            class Meta:
                managed = False

        field = Model._meta.get_field('name')
        field_type, _ = DjangoToPydanticFieldConverter(field).build_field()

        self.assertIn("max_length=30", str(field_type))

    def test_integerfield_validators_become_constraints(self):
        from django.core.validators import MinValueValidator, MaxValueValidator

        class Model(models.Model):
            count = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

            class Meta:
                managed = False

        field = Model._meta.get_field('count')
        field_type, _ = DjangoToPydanticFieldConverter(field).build_field()

        self.assertIn("ge=1", str(field_type))
        self.assertIn("le=10", str(field_type))

    def test_decimalfield_constraints_applied(self):
        class Model(models.Model):
            amount = models.DecimalField(max_digits=5, decimal_places=2)

            class Meta:
                managed = False

        field = Model._meta.get_field('amount')
        field_type, _ = DjangoToPydanticFieldConverter(field).build_field()

        self.assertIn("max_digits=5", str(field_type))
        self.assertIn("decimal_places=2", str(field_type))
