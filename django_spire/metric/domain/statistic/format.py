from __future__ import annotations

from decimal import Decimal

from django_spire.metric.domain.statistic.constants import StatisticValueTypeChoices


def _decimal_string(value: Decimal, places: int) -> str:
    return f'{value:,.{places}f}'


def format_statistic_value(
    value: Decimal | float | str, value_type: str = StatisticValueTypeChoices.NUMBER
) -> str:
    value = Decimal(str(value))

    if value_type == StatisticValueTypeChoices.CURRENCY:
        sign = '-' if value < 0 else ''
        return f'{sign}${_decimal_string(abs(value), 2)}'

    if value_type == StatisticValueTypeChoices.PERCENTAGE:
        return f'{_decimal_string(value, 2)}%'

    return _decimal_string(value, 2).rstrip('0').rstrip('.')
