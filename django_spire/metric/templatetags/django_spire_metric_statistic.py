from __future__ import annotations

from decimal import Decimal

from django.template import Library

from django_spire.metric.domain.statistic.constants import StatisticValueTypeChoices
from django_spire.metric.domain.statistic.format import format_statistic_value

register = Library()


@register.filter
def statistic_value(
    value: Decimal | float | str, value_type: str = StatisticValueTypeChoices.NUMBER
) -> str:
    return format_statistic_value(value, value_type)


@register.filter
def statistic_value_class(
    value: Decimal | float | str, value_type: str = StatisticValueTypeChoices.NUMBER
) -> str:
    if value_type != StatisticValueTypeChoices.CURRENCY:
        return ''

    value = Decimal(str(value))
    if value > 0:
        return 'text-success'
    if value < 0:
        return 'text-danger'

    return ''
