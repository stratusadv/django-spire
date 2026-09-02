from django.db import models


class VisualConditionStateChoices(models.TextChoices):
    GREEN = 'green', 'Green'
    BLUE = 'blue', 'Blue'
    YELLOW = 'yellow', 'Yellow'
    GREY = 'grey', 'Grey'
    RED = 'red', 'Red'


class VisualConditionOperatorChoices(models.TextChoices):
    GT = 'gt', 'Greater Than'
    GTE = 'gte', 'Greater Than or Equal'
    LT = 'lt', 'Less Than'
    LTE = 'lte', 'Less Than or Equal'
    EQ = 'eq', 'Equal To'
    BETWEEN = 'between', 'At or Near Target'


class VisualKindChoices(models.TextChoices):
    INDICATOR = 'indicator', 'Indicator'
    LINE = 'line', 'Line'
    BAR = 'bar', 'Bar'
    AREA = 'area', 'Area'
    PIE = 'pie', 'Pie'
    GAUGE = 'gauge', 'Gauge'
