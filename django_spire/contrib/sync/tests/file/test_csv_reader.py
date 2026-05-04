from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from django_spire.contrib.sync.file.exceptions import FileSyncParseError
from django_spire.contrib.sync.file.reader.csv import CsvReader

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def csv_file(tmp_path: Path) -> Path:
    content = dedent("""\
        StockNumber,Year,Make,Price
        13511,2021,Hyundai,226900.00
        16992,2024,Hyundai,0.00
    """)

    path = tmp_path / 'units.csv'
    path.write_text(content, encoding='utf-8')

    return path


@pytest.fixture
def tsv_file(tmp_path: Path) -> Path:
    content = dedent("""\
        StockNumber\tYear\tMake
        13511\t2021\tHyundai
    """)

    path = tmp_path / 'units.tsv'
    path.write_text(content, encoding='utf-8')

    return path


def test_parse_returns_list(csv_file: Path) -> None:
    reader = CsvReader()
    records = reader.read(csv_file)

    assert isinstance(records, list)


def test_record_count(csv_file: Path) -> None:
    reader = CsvReader()
    records = reader.read(csv_file)

    assert len(records) == 2


def test_record_fields(csv_file: Path) -> None:
    reader = CsvReader()
    records = reader.read(csv_file)

    assert records[0]['StockNumber'] == '13511'
    assert records[0]['Year'] == '2021'
    assert records[0]['Make'] == 'Hyundai'
    assert records[0]['Price'] == '226900.00'


def test_field_map(csv_file: Path) -> None:
    reader = CsvReader(
        field_map={
            'StockNumber': 'stock_number',
            'Year': 'year',
            'Make': 'make',
            'Price': 'price',
        },
    )

    records = reader.read(csv_file)

    assert 'stock_number' in records[0]
    assert 'year' in records[0]
    assert records[0]['stock_number'] == '13511'


def test_type_map(csv_file: Path) -> None:
    reader = CsvReader(
        field_map={
            'StockNumber': 'stock_number',
            'Year': 'year',
            'Price': 'price',
        },
        type_map={
            'year': int,
            'price': float,
        },
    )

    records = reader.read(csv_file)

    assert records[0]['year'] == 2021
    assert records[0]['price'] == 226900.00
    assert isinstance(records[0]['year'], int)
    assert isinstance(records[0]['price'], float)


def test_type_map_bad_value(tmp_path: Path) -> None:
    content = dedent("""\
        Name,Age
        Alice,N/A
    """)

    path = tmp_path / 'bad.csv'
    path.write_text(content, encoding='utf-8')

    reader = CsvReader(type_map={'Age': int})

    with pytest.raises(FileSyncParseError, match='Age'):
        reader.read(path)


def test_tsv_delimiter(tsv_file: Path) -> None:
    reader = CsvReader(delimiter='\t')
    records = reader.read(tsv_file)

    assert len(records) == 1
    assert records[0]['StockNumber'] == '13511'


def test_empty_file(tmp_path: Path) -> None:
    path = tmp_path / 'empty.csv'
    path.write_text('StockNumber,Year\n', encoding='utf-8')

    reader = CsvReader()
    records = reader.read(path)

    assert records == []


def test_field_map_preserves_unmapped(csv_file: Path) -> None:
    reader = CsvReader(
        field_map={'StockNumber': 'stock_number'},
    )

    records = reader.read(csv_file)

    assert 'stock_number' in records[0]
    assert 'Year' in records[0]
