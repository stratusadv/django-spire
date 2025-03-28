import datetime

from uuid import UUID

from django.db import models


MODEL_FIELD_TYPE_TO_TYPE_MAP = {
    models.AutoField.__name__: int,
    models.BigAutoField.__name__: int,
    models.SmallAutoField.__name__: int,
    models.BooleanField.__name__: bool,
    models.CharField.__name__: str,
    models.CommaSeparatedIntegerField.__name__: int,
    models.DateField.__name__: datetime.date,
    models.DateTimeField.__name__: datetime.datetime,
    models.DecimalField.__name__: float,
    models.DurationField.__name__: str,
    models.EmailField.__name__: str,
    models.FileField.__name__: str,
    models.FilePathField.__name__: str,
    models.FloatField.__name__: float,
    models.ForeignKey.__name__: int | UUID,
    models.OneToOneField.__name__: int | UUID,
    models.ManyToManyField.__name__: list[int],
    models.IntegerField.__name__: int,
    models.BigIntegerField.__name__: int,
    models.SmallIntegerField.__name__: int,
    models.IPAddressField.__name__: str,
    models.GenericIPAddressField.__name__: str,
    models.JSONField.__name__: dict | list,
    models.NullBooleanField.__name__: bool | None,
    models.PositiveBigIntegerField.__name__: int,
    models.PositiveIntegerField.__name__: int,
    models.PositiveSmallIntegerField.__name__: int,
    models.SlugField.__name__: str | UUID,
    models.TextField.__name__: str,
    models.TimeField.__name__: datetime.time,
    models.URLField.__name__: str,
    models.UUIDField.__name__: UUID,
}
