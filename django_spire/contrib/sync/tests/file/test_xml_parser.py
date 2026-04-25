from __future__ import annotations

from pathlib import Path

import pytest

from django_spire.contrib.sync.file.parser.xml import XmlField, XmlListField, XmlParser


FIXTURES_DIR = Path(__file__).parent / 'fixtures'


@pytest.fixture
def parser() -> XmlParser:
    return XmlParser(
        record_path='.//Unit',
        fields=[
            XmlField(key='stock_number', path='StockNumber'),
            XmlField(key='mfr_serial_number', path='MfrSerialNumber'),
            XmlField(key='type', path='Type'),
            XmlField(key='manufacturer', path='Manufacturer'),
            XmlField(key='description', path='Description'),
            XmlField(key='make_name', path='MakeName'),
            XmlField(key='model_name', path='ModelName'),
            XmlField(key='year', path='Year', cast=int, default='0'),
            XmlField(key='condition', path='Condition'),
            XmlField(key='price', path='Price', cast=float, default='0'),
            XmlField(key='meter', path='Meter', cast=float, default='0'),
            XmlField(key='meter_unit', path='MeterUnit'),
            XmlField(key='misc_1', path='Misc1'),
            XmlField(key='misc_2', path='Misc2'),
            XmlField(key='public_comment', path='PublicComment'),
            XmlField(key='location_name', path='Location/Name'),
            XmlField(key='location_city', path='Location/City'),
            XmlField(key='location_state_code', path='Location/StateCode'),
            XmlField(key='location_zip_code', path='Location/ZipCode'),
            XmlField(key='location_phone', path='Location/Phone'),
            XmlListField(key='images', path='Images/Image'),
        ],
    )


def test_unit_count(parser: XmlParser) -> None:
    units = parser.parse(FIXTURES_DIR / 'sample_units.xml')

    assert len(units) == 2


def test_unit_fields(parser: XmlParser) -> None:
    units = parser.parse(FIXTURES_DIR / 'sample_units.xml')
    unit = units[0]

    assert unit['stock_number'] == '13511'
    assert unit['mfr_serial_number'] == 'HHKHW770VL0000178'
    assert unit['type'] == 'Wheel Loader'
    assert unit['manufacturer'] == 'Hyundai'
    assert unit['make_name'] == 'HYUNDAI'
    assert unit['model_name'] == 'HL975'
    assert unit['year'] == 2021
    assert unit['condition'] == 'Used'
    assert unit['price'] == 226900.00
    assert unit['meter'] == 6078.0
    assert unit['meter_unit'] == 'hours'
    assert unit['misc_2'] == 'No'


def test_location(parser: XmlParser) -> None:
    units = parser.parse(FIXTURES_DIR / 'sample_units.xml')
    unit = units[0]

    assert unit['location_name'] == 'Chinook Equipment'
    assert unit['location_city'] == 'Lethbridge County'
    assert unit['location_state_code'] == 'AB'
    assert unit['location_zip_code'] == 'T1J 5X8'
    assert unit['location_phone'] == '(403) 329-6011 x'


def test_images(parser: XmlParser) -> None:
    units = parser.parse(FIXTURES_DIR / 'sample_units.xml')

    assert units[0]['images'] == []
    assert len(units[1]['images']) == 3
    assert units[1]['images'][0] == 'Img5066-16992-1.png'


def test_empty_units(parser: XmlParser) -> None:
    units = parser.parse(FIXTURES_DIR / 'empty_units.xml')

    assert units == []


def test_missing_fields_default(parser: XmlParser) -> None:
    units = parser.parse(FIXTURES_DIR / 'missing_fields_units.xml')
    unit = units[0]

    assert unit['stock_number'] == '99999'
    assert unit['year'] == 0
    assert unit['price'] == 0.0
    assert unit['manufacturer'] == ''
    assert unit['images'] == []
    assert unit['location_name'] == ''


def test_empty_elements(parser: XmlParser) -> None:
    units = parser.parse(FIXTURES_DIR / 'sample_units.xml')

    assert units[0]['misc_1'] == ''
    assert units[0]['public_comment'] == ''
