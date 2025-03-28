# from django.test.testcases import TestCase
#
# from django.db import models
#
# from django_spire.core.converters.to_pydantic.factories import DjangoFieldToPydanticFieldFactory
#
#
# class DjangoModel(models.Model):
#     name = models.CharField(
#         max_length=255,
#         default='',
#         help_text='Name of a Person',
#         unique=True
#
#     ) # null, blank, choices, help_text, unique, verbose_name,
#     description = models.TextField(default='')
#     age = models.IntegerField()
#     height = models.FloatField()
#     birth_date = models.DateField()
#
#     @classmethod
#     def get_field_by_name(cls, field_name):
#         for field in cls._meta.fields:
#             if field.name == field_name:
#                 return field
#         return None
#

# class DjangoToPydanticModelTestCase(TestCase):
#
#     def test_django_model_to_pydantic_model(self):
#         print('hi')
#         self.assertTrue(True)
#
#
#
# class DjangoFieldToPydanticFieldTestCase(TestCase):
#
#     def setUp(self):
#         self.django_model = DjangoModel
#
#     def test_django_char_field_to_pydantic(self):
#         char_field = self.django_model.get_field_by_name('name')
#         pydantic_field_factory = DjangoFieldToPydanticFieldFactory(char_field)
#         pydantic_char_field = pydantic_field_factory.build_field()
#         self.assertEqual(pydantic_char_field.type_, 'str')
