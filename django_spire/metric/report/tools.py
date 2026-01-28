import datetime

from django_spire.metric.report.enums import ColumnType


def get_text_alignment_css_class(column_type: ColumnType) -> str:
    if column_type in (ColumnType.DOLLAR, ColumnType.NUMBER, ColumnType.PERCENT, ColumnType.DECIMAL_1,
                     ColumnType.DECIMAL_2, ColumnType.DECIMAL_3):
        return 'text-end'
    if column_type == ColumnType.CHOICE:
        return 'text-center'

    return 'text-start'
