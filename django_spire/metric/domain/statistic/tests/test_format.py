from __future__ import annotations

from decimal import Decimal

import pytest

from django.template import Template, Context

from django_spire.metric.domain.statistic.constants import StatisticValueTypeChoices
from django_spire.metric.domain.statistic.format import format_statistic_value


class TestFormatStatisticValue:
    @pytest.mark.parametrize(
        ('value', 'value_type', 'expected'),
        [
            (5, StatisticValueTypeChoices.NUMBER, '5'),
            (Decimal('5.10'), StatisticValueTypeChoices.NUMBER, '5.1'),
            (Decimal('1234.5678'), StatisticValueTypeChoices.NUMBER, '1,234.57'),
            (0, StatisticValueTypeChoices.NUMBER, '0'),
            (Decimal('1234.5'), StatisticValueTypeChoices.CURRENCY, '$1,234.50'),
            (Decimal('-1234.5'), StatisticValueTypeChoices.CURRENCY, '-$1,234.50'),
            (0, StatisticValueTypeChoices.CURRENCY, '$0.00'),
            (Decimal('12.345'), StatisticValueTypeChoices.PERCENTAGE, '12.34%'),
            (Decimal('1234.5'), StatisticValueTypeChoices.PERCENTAGE, '1,234.50%'),
            (5, None, '5'),
        ],
    )
    def test_format_statistic_value(
        self, value: Decimal | int, value_type: str | None, expected: str
    ):
        assert format_statistic_value(value, value_type) == expected


class TestStatisticValueTemplateFilter:
    @pytest.mark.parametrize(
        ('value', 'value_type', 'expected'),
        [
            ('1234.5', 'currency', '$1,234.50'),
            ('12.345', 'percentage', '12.34%'),
            ('1234.5678', 'number', '1,234.57'),
        ],
    )
    def test_statistic_value_filter(self, value: str, value_type: str, expected: str):
        template = Template(
            '{% load django_spire_metric_statistic %}{{ value|statistic_value:value_type }}'
        )
        rendered = template.render(Context({'value': value, 'value_type': value_type}))
        assert rendered == expected


class TestStatisticValueClassFilter:
    @pytest.mark.parametrize(
        ('value', 'value_type', 'expected'),
        [
            ('1234.5', 'currency', 'text-success'),
            ('-1234.5', 'currency', 'text-danger'),
            ('0', 'currency', ''),
            ('1234.5', 'number', ''),
            ('12.5', 'percentage', ''),
        ],
    )
    def test_statistic_value_class_filter(self, value: str, value_type: str, expected: str):
        template = Template(
            '{% load django_spire_metric_statistic %}{{ value|statistic_value_class:value_type }}'
        )
        rendered = template.render(Context({'value': value, 'value_type': value_type}))
        assert rendered == expected
