from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.ordering.exceptions import OrderingMixinExceptionGroup
from django_spire.contrib.ordering.validators import OrderingMixinValidator
from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet
    from django_spire.contrib.ordering.mixins import OrderingModelMixin


class OrderingProcessorService(BaseDjangoModelService['OrderingModelMixin']):
    obj: OrderingModelMixin

    def _reorder_objects(self, objects: QuerySet[Model]):
        for index, item in enumerate(objects):
            item.order = index

        self.obj_class.objects.bulk_update(objects, ['order'])

    def _reorder_destination_and_origin_objects(
        self,
        destination_objects: QuerySet[Model],
        origin_objects: QuerySet[Model],
        insert_position: int,
    ):
        self._reorder_objects(origin_objects)

        # Forces destination objects to refresh in the event they overlap the origin objects
        destination_objects = destination_objects.all()

        for index, item in enumerate(destination_objects):
            if item.order >= insert_position:
                item.order = index + 1

        self.obj_class.objects.bulk_update(destination_objects, ['order'])

    def move_to_position(
        self,
        destination_objects: QuerySet[Model],
        position: int,
        origin_objects: QuerySet[Model],
    ):
        ordering_mixin_validator = OrderingMixinValidator(
            destination_objects=destination_objects,
            position=position,
            obj=self.obj,
            origin_objects=origin_objects,
        )

        if not ordering_mixin_validator.validate():
            raise OrderingMixinExceptionGroup(
                'Ordering validation failed.',
                ordering_mixin_validator.errors
            )

        destination_objects = destination_objects.exclude(pk=self.obj.pk).order_by('order')
        origin_objects = origin_objects.exclude(pk=self.obj.pk).order_by('order')

        self._reorder_destination_and_origin_objects(
            destination_objects=destination_objects,
            origin_objects=origin_objects,
            insert_position=position,
        )

        self.obj.order = position
        self.obj.save(update_fields=['order'])

    def remove_from_objects(
        self,
        destination_objects: QuerySet[Model],
    ):
        ordering_mixin_validator = OrderingMixinValidator(
            destination_objects=destination_objects,
            position=0,
            obj=self.obj,
            origin_objects=destination_objects,
        )

        if not ordering_mixin_validator.validate():
            raise ExceptionGroup(
                'Ordering validation failed.',
                ordering_mixin_validator.errors
            )

        destination_objects = destination_objects.exclude(pk=self.obj.pk).order_by('order')

        self._reorder_objects(objects=destination_objects)
