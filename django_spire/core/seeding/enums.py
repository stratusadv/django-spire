from django.db import models
from enum import Enum

import datetime
from decimal import Decimal
from typing import Union, Optional
from uuid import UUID


class FieldType(str, Enum):
    AUTO_FIELD = models.AutoField.__name__
    BIG_AUTO_FIELD = models.BigAutoField.__name__
    SMALL_AUTO_FIELD = models.SmallAutoField.__name__
    BOOLEAN = models.BooleanField.__name__
    CHAR = models.CharField.__name__
    COMMA_SEPARATED_INTEGER = models.CommaSeparatedIntegerField.__name__
    DATE = models.DateField.__name__
    DATETIME = models.DateTimeField.__name__
    DECIMAL = models.DecimalField.__name__
    DURATION = models.DurationField.__name__
    EMAIL = models.EmailField.__name__
    FILE = models.FileField.__name__
    FILE_PATH = models.FilePathField.__name__
    FLOAT = models.FloatField.__name__
    FOREIGN_KEY = models.ForeignKey.__name__
    ONE_TO_ONE = models.OneToOneField.__name__
    MANY_TO_MANY = models.ManyToManyField.__name__
    INTEGER = models.IntegerField.__name__
    BIG_INTEGER = models.BigIntegerField.__name__
    SMALL_INTEGER = models.SmallIntegerField.__name__
    IP_ADDRESS = models.IPAddressField.__name__
    GENERIC_IP_ADDRESS = models.GenericIPAddressField.__name__
    JSON = models.JSONField.__name__
    NULL_BOOLEAN = models.NullBooleanField.__name__
    POSITIVE_BIG_INTEGER = models.PositiveBigIntegerField.__name__
    POSITIVE_INTEGER = models.PositiveIntegerField.__name__
    POSITIVE_SMALL_INTEGER = models.PositiveSmallIntegerField.__name__
    SLUG = models.SlugField.__name__
    TEXT = models.TextField.__name__
    TIME = models.TimeField.__name__
    URL = models.URLField.__name__
    UUID = models.UUIDField.__name__



FIELD_TYPE_TO_TYPE_HINTING = {
    FieldType.AUTO_FIELD: int,
    FieldType.BIG_AUTO_FIELD: int,
    FieldType.SMALL_AUTO_FIELD: int,
    FieldType.BOOLEAN: bool,
    FieldType.CHAR: str,
    FieldType.COMMA_SEPARATED_INTEGER: int,
    FieldType.DATE: datetime.date,
    FieldType.DATETIME: datetime.datetime,
    FieldType.DECIMAL: Decimal,
    FieldType.DURATION: str,
    FieldType.EMAIL: str,
    FieldType.FLOAT: float,
    FieldType.INTEGER: int,
    FieldType.BIG_INTEGER: int,
    FieldType.SMALL_INTEGER: int,
    FieldType.GENERIC_IP_ADDRESS: str,
    FieldType.IP_ADDRESS: str,
    FieldType.FOREIGN_KEY: int,
    FieldType.ONE_TO_ONE: int,
    FieldType.MANY_TO_MANY: list[int],
    FieldType.JSON: Union[dict, list],
    FieldType.NULL_BOOLEAN: Optional[bool],  # Now depreciated in django
    FieldType.POSITIVE_BIG_INTEGER: int,
    FieldType.POSITIVE_INTEGER: int,
    FieldType.POSITIVE_SMALL_INTEGER: int,
    FieldType.SLUG: str,
    FieldType.TEXT: str,
    FieldType.TIME: datetime.time,
    FieldType.URL: str,
    FieldType.UUID: UUID
}
