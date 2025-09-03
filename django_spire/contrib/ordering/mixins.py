from django.db import models

from django_spire.contrib.ordering.services.service import OrderingService


class OrderingModelMixin(models.Model):
    order = models.PositiveIntegerField(
        default=0
    )

    ordering_services = OrderingService()

    class Meta:
        abstract = True
