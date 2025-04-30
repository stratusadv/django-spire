from __future__ import annotations

import json

from django.test import RequestFactory

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.core.shortcuts import (
    get_object_or_none,
    get_object_or_null_obj,
    model_object_from_app_label,
    process_request_body
)

# from testing.dummy.models import DummyModel
#
#
# class ShortcutsTestCase(BaseTestCase):
#     def setUp(self) -> None:
#         super().setUp()
#
#         self.dummy = DummyModel.objects.create(name='test')
#         self.request_factory = RequestFactory()
#
#     def test_get_object_or_null_obj_queryset_found(self) -> None:
#         obj = get_object_or_null_obj(DummyModel.objects.all(), name='test')
#         self.assertEqual(obj, self.dummy)
#
#     def test_get_object_or_null_obj_queryset_not_found(self) -> None:
#         obj = get_object_or_null_obj(DummyModel.objects.all(), name='nonexistent')
#         self.assertIsNone(obj.pk)
#         self.assertEqual(obj.name, '')
#
#     def test_get_object_or_null_obj_model_found(self) -> None:
#         obj = get_object_or_null_obj(DummyModel, name='test')
#         self.assertEqual(obj, self.dummy)
#
#     def test_get_object_or_null_obj_model_not_found(self) -> None:
#         obj = get_object_or_null_obj(DummyModel, name='nonexistent')
#         self.assertIsNone(obj.pk)
#         self.assertEqual(obj.name, '')
#
#     def test_get_object_or_none_found(self) -> None:
#         obj = get_object_or_none(DummyModel, pk=self.dummy.pk)
#         self.assertEqual(obj, self.dummy)
#
#     def test_get_object_or_none_not_found(self) -> None:
#         obj = get_object_or_none(DummyModel, pk=9999)
#         self.assertIsNone(obj)
#
#     def test_process_request_body(self) -> None:
#         data = {'data': {'key': 'value'}}
#
#         request = self.request_factory.post(
#             '/dummy-url/',
#             data=json.dumps(data),
#             content_type='application/json'
#         )
#
#         result = process_request_body(request)
#         self.assertEqual(result, data['data'])
#
#     def test_model_object_from_app_label_found(self) -> None:
#         obj = model_object_from_app_label('dummy', 'dummymodel', self.dummy.pk)
#         self.assertEqual(obj, self.dummy)
#
#     def test_model_object_from_app_label_not_found(self) -> None:
#         obj = model_object_from_app_label('dummy', 'dummymodel', 9999)
#         self.assertIsNone(obj)
#
#     def test_model_object_from_app_label_contenttype_not_found(self) -> None:
#         obj = model_object_from_app_label('nonexistent', 'nonexistent', 1)
#         self.assertIsNone(obj)
