import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import Literal, Callable, Any

from django_spire.metric.report.enums import ColumnType
from django_spire.metric.report.helper import Helper
from django_spire.metric.report.tools import get_text_alignment_css_class

ColumnLiteralType = Literal['text', 'choice', 'number', 'dollar', 'percent']


@dataclass
class ReportColumn:
    title: str
    sub_title: str | None = None
    type: ColumnType = ColumnType.TEXT
    sub_type: ColumnType = ColumnType.TEXT

    def css_class(self) -> str:
        return get_text_alignment_css_class(self.type)


@dataclass
class ReportCell:
    value: Any
    sub_value: Any = None
    type: ColumnType = ColumnType.TEXT
    sub_type: ColumnType = ColumnType.TEXT

    def css_class(self) -> str:
        return get_text_alignment_css_class(self.type)

    @staticmethod
    def cell_value_verbose(value, cell_type):
        if cell_type == ColumnType.DOLLAR:
            return f"${float(value):,.2f}"
        elif cell_type == ColumnType.NUMBER:
            return f"{float(value):,.0f}"
        elif cell_type == ColumnType.PERCENT:
            return f"{float(value):.1f}%"
        elif cell_type == ColumnType.DECIMAL_1:
            return f"{float(value):.1f}"
        elif cell_type == ColumnType.DECIMAL_2:
            return f"{float(value):.2f}"
        elif cell_type == ColumnType.DECIMAL_3:
            return f"{float(value):.3f}"

        return str(value)

    def value_verbose(self):
        return self.cell_value_verbose(self.value, self.type)

    def sub_value_verbose(self):
        return self.cell_value_verbose(self.sub_value, self.sub_type)


@dataclass
class ReportRow:
    cells: list[ReportCell] = field(default_factory=list)
    bold: bool = False
    page_break: bool = False
    span_all_columns: bool = False
    table_break: bool = False
    border_top: bool = False
    border_bottom: bool = False


class BaseReport(ABC):
    title: str
    description: str | None = None
    is_financially_accurate: bool = False
    ColumnType: type[ColumnType] = ColumnType
    helper: Helper = Helper()

    def __init__(self):
        if not self.title:
            message = 'Report title is required'
            raise ValueError(message)

        self.columns: list[ReportColumn] = []
        self.rows: list[ReportRow] = []

    @property
    def column_count(self) -> int:
        return len(self.columns)

    @property
    def is_ready(self):
        return len(self.columns) > 0

    @property
    def run_arguments(self) -> dict[str, dict[str, str]]:
        arguments = {}
        signature = inspect.signature(self.run)

        for name, param in signature.parameters.items():
            arguments[name] = {}
            arguments[name]['default'] = param.default

            choices_method = getattr(self, f'{name}_choices', None)

            if choices_method and isinstance(choices_method, Callable):
                choices = tuple(choices_method())

                self.validate_choices(tuple(choices))

                arguments[name]['choices'] = choices
                if param.annotation.__name__ == 'list':
                    arguments[name]['annotation'] = 'multi_select'
                else:
                    arguments[name]['annotation'] = 'select'
            else:
                arguments[name]['annotation'] = param.annotation.__name__

        return arguments

    @abstractmethod
    def run(self, **kwargs: Any):
        raise NotImplementedError

    def add_blank_row(
            self,
            text: str = '',
            page_break: bool = False,
            border_top: bool = False,
            border_bottom: bool = False
    ):
        self.add_row(
            cell_values=[
                text
            ],
            span_all_columns=True,
            page_break=page_break,
            border_top=border_top,
            border_bottom=border_bottom,
        )

    def add_column(
            self,
            title: str,
            sub_title: str | None = None,
            type: ColumnType = ColumnType.TEXT,
            sub_type: ColumnType = ColumnType.TEXT,

    ):
        self.columns.append(
            ReportColumn(title=title, sub_title=sub_title, type=type, sub_type=sub_type)
        )

    def add_divider_row(
            self,
            title: str,
            description: str | None = None,
            page_break: bool = False,
            border_bottom: bool = True,
    ):
        self.add_row(
            cell_values=[title],
            cell_sub_values=[description] if description else None,
            bold=True,
            page_break=page_break,
            span_all_columns=True,
            border_bottom=border_bottom,
        )

    def add_footer_row(
            self,
            cell_values: list[Any],
            cell_sub_values: list[Any] | None = None,
            border_top: bool = True,
    ):
        self.add_row(
            cell_values=cell_values,
            cell_sub_values=cell_sub_values,
            bold=True,
            border_top=border_top,
        )

    def add_row(
            self,
            cell_values: list[Any],
            cell_sub_values: list[Any] | None = None,
            bold: bool = False,
            page_break: bool = False,
            span_all_columns: bool = False,
            table_break: bool = False,
            border_top: bool = False,
            border_bottom: bool = False,
    ):
        if span_all_columns or table_break:
            if len(cell_values) > 1:
                message = 'Cannot span all columns or have a table break with more than one cell value'
                raise ValueError(message)

        elif len(cell_values) != len(self.columns) or (
                cell_sub_values is not None and len(cell_sub_values) != len(self.columns)):
            message = f'Number of cell values ({len(cell_values)}) and sub values ({len(cell_sub_values) if cell_sub_values else "None"}) must match number of columns: {len(self.columns)}'
            raise ValueError(message)

        self.rows.append(
            ReportRow(
                cells=[
                    ReportCell(
                        value=cell_values[i],
                        sub_value=cell_sub_values[i] if cell_sub_values else None,
                        type=self.columns[i].type,
                        sub_type=self.columns[i].sub_type
                    )
                    for i in range(len(cell_values))
                ],
                bold=bold,
                page_break=page_break,
                span_all_columns=span_all_columns,
                table_break=table_break,
                border_top=border_top,
                border_bottom=border_bottom,
            )
        )

    @staticmethod
    def validate_choices(choices: tuple):
        if not isinstance(choices, tuple):
            raise TypeError(f'choices must be a tuple not {type(choices)}')
        if not all(isinstance(item, tuple) and len(item) == 2 for item in choices):
            raise ValueError('choices must contain tuples of length 2')

    def to_markdown(self) -> str:
        markdown = ''

        for column in self.columns:
            markdown += f'| {column.title} '

        markdown += '|\n'

        for column in self.columns:
            markdown += '| ' + '-' * len(column.title) + ' '

        markdown += '|\n'

        for row in self.rows:
            if row.span_all_columns:
                markdown += f'| {row.cells[0].value}' + '|' * len(self.columns) + '\n'
                continue

            else:
                for cell in row.cells:
                    markdown += f'| {cell.value_verbose()} '

            markdown += '|\n'

        return markdown
