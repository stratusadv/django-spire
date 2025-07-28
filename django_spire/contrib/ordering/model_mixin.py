from django.db import models


class OrderingModelMixin(models.Model):
    order = models.PositiveIntegerField(
        default=0,
        editable=False
    )