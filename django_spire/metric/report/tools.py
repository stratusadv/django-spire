from django_spire.metric.report.enums import ColumnType


def get_text_alignment_css_class(column_type: ColumnType) -> str:
    if column_type in (
            ColumnType.DOLLAR,
            ColumnType.DOLLAR_1,
            ColumnType.DOLLAR_2,
            ColumnType.DOLLAR_3,
            ColumnType.PERCENT,
            ColumnType.PERCENT_1,
            ColumnType.PERCENT_2,
            ColumnType.PERCENT_3,
            ColumnType.NUMBER,
            ColumnType.NUMBER_1,
            ColumnType.NUMBER_2,
            ColumnType.NUMBER_3
    ):
        return 'text-end'
    if column_type == ColumnType.CHOICE:
        return 'text-center'

    return 'text-start'
