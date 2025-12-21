from __future__ import annotations

import pytest

from unittest.mock import MagicMock

from django.test import TestCase

from django_spire.contrib.ordering.exceptions import OrderingMixinError, OrderingMixinGroupError
from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.contrib.ordering.services.processor_service import OrderingProcessorService
from django_spire.contrib.ordering.services.service import OrderingService
from django_spire.contrib.ordering.validators import OrderingMixinValidator


class TestOrderingMixinError(TestCase):
    def test_can_be_raised(self) -> None:
        with pytest.raises(OrderingMixinError):
            message = 'Test'
            raise OrderingMixinError(message)

    def test_is_exception(self) -> None:
        assert issubclass(OrderingMixinError, Exception)

    def test_message(self) -> None:
        error = OrderingMixinError('Test error message')

        assert str(error) == 'Test error message'


class TestOrderingMixinGroupError(TestCase):
    def test_can_be_raised(self) -> None:
        with pytest.raises(OrderingMixinGroupError):
            message = 'Test'
            raise OrderingMixinGroupError(message)

    def test_is_exception(self) -> None:
        assert issubclass(OrderingMixinGroupError, Exception)

    def test_message(self) -> None:
        error = OrderingMixinGroupError('Test group error message')

        assert str(error) == 'Test group error message'


class TestOrderingMixinValidator(TestCase):
    def setUp(self) -> None:
        self.obj = MagicMock()
        self.obj.pk = 1

        self.destination_objects = MagicMock()
        self.destination_objects.__len__ = MagicMock(return_value=5)

        self.origin_objects = MagicMock()
        self.origin_objects.__len__ = MagicMock(return_value=5)

    def test_errors_contain_ordering_mixin_error(self) -> None:
        validator = OrderingMixinValidator(
            destination_objects=self.destination_objects,
            position=-1,
            obj=self.obj,
            origin_objects=self.origin_objects
        )

        validator.validate()

        assert all(isinstance(error, OrderingMixinError) for error in validator.errors)

    def test_errors_property_returns_list(self) -> None:
        validator = OrderingMixinValidator(
            destination_objects=self.destination_objects,
            position=0,
            obj=self.obj,
            origin_objects=self.origin_objects
        )

        assert isinstance(validator.errors, list)

    def test_validate_position_at_boundary(self) -> None:
        validator = OrderingMixinValidator(
            destination_objects=self.destination_objects,
            position=5,
            obj=self.obj,
            origin_objects=self.origin_objects
        )

        assert validator.validate() is True

    def test_validate_position_zero(self) -> None:
        validator = OrderingMixinValidator(
            destination_objects=self.destination_objects,
            position=0,
            obj=self.obj,
            origin_objects=self.origin_objects
        )

        assert validator.validate() is True

    def test_validate_returns_false_for_negative_position(self) -> None:
        validator = OrderingMixinValidator(
            destination_objects=self.destination_objects,
            position=-1,
            obj=self.obj,
            origin_objects=self.origin_objects
        )

        assert validator.validate() is False
        assert len(validator.errors) == 1

    def test_validate_returns_false_for_position_greater_than_objects(self) -> None:
        validator = OrderingMixinValidator(
            destination_objects=self.destination_objects,
            position=10,
            obj=self.obj,
            origin_objects=self.origin_objects
        )

        assert validator.validate() is False
        assert len(validator.errors) == 1

    def test_validate_returns_true_for_valid_position(self) -> None:
        validator = OrderingMixinValidator(
            destination_objects=self.destination_objects,
            position=2,
            obj=self.obj,
            origin_objects=self.origin_objects
        )

        assert validator.validate() is True


class TestOrderingModelMixin(TestCase):
    def test_has_order_field(self) -> None:
        assert hasattr(OrderingModelMixin, 'order')

    def test_has_ordering_services_in_dict(self) -> None:
        assert 'ordering_services' in OrderingModelMixin.__dict__

    def test_is_abstract(self) -> None:
        assert OrderingModelMixin._meta.abstract is True

    def test_order_default_value(self) -> None:
        assert OrderingModelMixin._meta.get_field('order').default == 0


class TestOrderingProcessorService(TestCase):
    def test_has_move_to_position_method(self) -> None:
        assert hasattr(OrderingProcessorService, 'move_to_position')

    def test_has_remove_from_objects_method(self) -> None:
        assert hasattr(OrderingProcessorService, 'remove_from_objects')

    def test_has_reorder_destination_and_origin_objects_method(self) -> None:
        assert hasattr(OrderingProcessorService, '_reorder_destination_and_origin_objects')

    def test_has_reorder_objects_method(self) -> None:
        assert hasattr(OrderingProcessorService, '_reorder_objects')


class TestOrderingService(TestCase):
    def test_has_processor_in_dict(self) -> None:
        assert 'processor' in OrderingService.__dict__

    def test_processor_in_dict_is_ordering_processor_service(self) -> None:
        assert isinstance(OrderingService.__dict__['processor'], OrderingProcessorService)
