from __future__ import annotations

import importlib

import pytest

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.utils import (
    format_size,
    SIZE_BYTES_PER_KB,
    SIZE_BYTES_PER_MB,
    SIZE_BYTES_PER_GB,
    SIZE_BYTES_PER_TB,
)

_migration = importlib.import_module(
    'django_spire.file.migrations.0002_alter_file_related_field_alter_file_size'
)

_parse_size = _migration._parse_size
SIZE_MULTIPLIERS = _migration.SIZE_MULTIPLIERS
REVERSE_THRESHOLDS = _migration.REVERSE_THRESHOLDS


class ParseSizeFormattedStringTests(BaseTestCase):
    def test_kb_lowercase(self) -> None:
        assert _parse_size('0.91 kb') == int(0.91 * 1_024)

    def test_kb_uppercase(self) -> None:
        assert _parse_size('0.91 KB') == int(0.91 * 1_024)

    def test_kb_mixed_case(self) -> None:
        assert _parse_size('0.91 Kb') == int(0.91 * 1_024)

    def test_mb_lowercase(self) -> None:
        assert _parse_size('3.12 mb') == int(3.12 * 1_048_576)

    def test_mb_uppercase(self) -> None:
        assert _parse_size('3.12 MB') == int(3.12 * 1_048_576)

    def test_gb_lowercase(self) -> None:
        assert _parse_size('1.5 gb') == int(1.5 * 1_073_741_824)

    def test_gb_uppercase(self) -> None:
        assert _parse_size('1.5 GB') == int(1.5 * 1_073_741_824)

    def test_tb_lowercase(self) -> None:
        assert _parse_size('2.0 tb') == int(2.0 * 1_099_511_627_776)

    def test_tb_uppercase(self) -> None:
        assert _parse_size('2.0 TB') == int(2.0 * 1_099_511_627_776)

    def test_whole_number_with_unit(self) -> None:
        assert _parse_size('5 KB') == 5 * 1_024

    def test_zero_with_unit(self) -> None:
        assert _parse_size('0 KB') == 0

    def test_large_decimal_with_unit(self) -> None:
        assert _parse_size('109.23 kb') == int(109.23 * 1_024)


class ParseSizeRawBytesTests(BaseTestCase):
    def test_integer_string(self) -> None:
        assert _parse_size('36209') == 36_209

    def test_zero_string(self) -> None:
        assert _parse_size('0') == 0

    def test_large_integer_string(self) -> None:
        assert _parse_size('1048576') == 1_048_576

    def test_float_string_truncates(self) -> None:
        assert _parse_size('1024.5') == 1_024

    def test_single_byte(self) -> None:
        assert _parse_size('1') == 1


class ParseSizeInvalidInputTests(BaseTestCase):
    def test_unknown_unit_returns_none(self) -> None:
        assert _parse_size('5 XB') is None

    def test_three_parts_returns_none(self) -> None:
        assert _parse_size('5 KB extra') is None

    def test_non_numeric_value_with_unit_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('abc KB')

    def test_non_numeric_single_value_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('abc')

    def test_empty_unit_returns_none(self) -> None:
        assert _parse_size('5  ') is None

    def test_unit_only_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size(' KB')

    def test_multiple_spaces_between_value_and_unit(self) -> None:
        assert _parse_size('5  KB') is None

    def test_tab_between_value_and_unit_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('5\tKB')


class ParseSizeFloatingPointTests(BaseTestCase):
    def test_many_decimal_places(self) -> None:
        result = _parse_size('1.123456789 KB')

        assert isinstance(result, int)
        assert result == int(1.123456789 * 1_024)

    def test_trailing_zeros(self) -> None:
        assert _parse_size('1.00 KB') == 1_024

    def test_point_zero(self) -> None:
        assert _parse_size('0.0 KB') == 0

    def test_very_small_decimal(self) -> None:
        result = _parse_size('0.001 KB')

        assert result == int(0.001 * 1_024)
        assert result > 0

    def test_scientific_notation_raw(self) -> None:
        result = _parse_size('1e3')

        assert result == 1_000

    def test_scientific_notation_with_unit(self) -> None:
        result = _parse_size('1e3 KB')

        assert result == int(1e3 * 1_024)

    def test_negative_raw_bytes(self) -> None:
        result = _parse_size('-100')

        assert result == -100

    def test_negative_with_unit(self) -> None:
        result = _parse_size('-5 KB')

        assert result == (-5 * 1_024)


class ParseSizeUnicodeAndEncodingTests(BaseTestCase):
    def test_non_breaking_space_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('5\u00a0KB')

    def test_en_space_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('5\u2002KB')

    def test_unicode_digit_parses(self) -> None:
        result = _parse_size('\u0661\u0662 KB')

        assert result == (12 * 1_024)

    def test_fullwidth_digit_parses(self) -> None:
        result = _parse_size('\uff15 KB')

        assert result == (5 * 1_024)

    def test_comma_formatted_number_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('1,024 KB')

    def test_null_byte_in_value_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('5\x00 KB')

    def test_bom_prefix_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('\ufeff5 KB')


class ParseSizeBoundaryTests(BaseTestCase):
    def test_max_positive_big_integer_loses_precision(self) -> None:
        large = str(2**63 - 1)
        result = _parse_size(large)

        assert result == int(float(large))

    def test_zero_point_zero_raw(self) -> None:
        assert _parse_size('0.0') == 0

    def test_just_a_dot_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('.')

    def test_dot_with_unit_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('. KB')

    def test_plus_sign_prefix(self) -> None:
        assert _parse_size('+100') == 100

    def test_plus_sign_with_unit(self) -> None:
        assert _parse_size('+5 KB') == 5 * 1_024

    def test_double_negative_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('--5')

    def test_inf_raw_raises(self) -> None:
        with pytest.raises(OverflowError):
            _parse_size('inf')

    def test_inf_with_unit_raises(self) -> None:
        with pytest.raises(OverflowError):
            _parse_size('inf KB')

    def test_nan_raw_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('nan')

    def test_nan_with_unit_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('nan KB')

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError):  # noqa: PT011
            _parse_size('')

    def test_single_space_returns_none(self) -> None:
        assert _parse_size(' ') is None


class ParseSizePartialUnitTests(BaseTestCase):
    def test_lowercase_b_alone_returns_none(self) -> None:
        assert _parse_size('5 b') is None

    def test_bytes_spelled_out_returns_none(self) -> None:
        assert _parse_size('5 bytes') is None

    def test_kib_returns_none(self) -> None:
        assert _parse_size('5 KiB') is None

    def test_mib_returns_none(self) -> None:
        assert _parse_size('5 MiB') is None

    def test_k_alone_returns_none(self) -> None:
        assert _parse_size('5 K') is None

    def test_m_alone_returns_none(self) -> None:
        assert _parse_size('5 M') is None


class ParseSizeRoundTripTests(BaseTestCase):
    def test_kb_round_trip(self) -> None:
        original = '0.91 kb'
        size_bytes = _parse_size(original)

        assert format_size(size_bytes) == '0.91 KB'

    def test_mb_round_trip(self) -> None:
        original = '1.0 mb'
        size_bytes = _parse_size(original)

        assert format_size(size_bytes) == '1.0 MB'

    def test_gb_round_trip(self) -> None:
        original = '1.0 gb'
        size_bytes = _parse_size(original)

        assert format_size(size_bytes) == '1.0 GB'

    def test_tb_round_trip(self) -> None:
        original = '1.0 tb'
        size_bytes = _parse_size(original)

        assert format_size(size_bytes) == '1.0 TB'

    def test_raw_bytes_round_trip_stays_positive(self) -> None:
        size_bytes = _parse_size('36209')

        assert size_bytes == 36_209
        assert 'KB' in format_size(size_bytes)

    def test_production_formatted_values_round_trip(self) -> None:
        production_sizes = [
            '0.91 kb', '3.12 kb', '3.87 kb', '0.59 kb',
            '0.02 kb', '0.92 kb', '4.03 kb', '6.1 kb',
            '18.01 kb', '5.02 kb', '10.04 kb', '3.56 kb',
            '1.92 kb', '9.63 kb', '9.61 kb', '17.46 kb',
            '109.23 kb', '83.75 kb', '3.71 kb', '5.46 kb',
            '4.97 kb',
        ]

        for original in production_sizes:
            size_bytes = _parse_size(original)
            formatted = format_size(size_bytes)
            value = original.strip().split(' ')[0]

            assert formatted == f'{value} KB'

    def test_production_raw_byte_values(self) -> None:
        raw_sizes = ['36209', '36221']

        for raw in raw_sizes:
            size_bytes = _parse_size(raw)

            assert size_bytes == int(raw)
            assert size_bytes > 0

    def test_sub_kb_value_does_not_survive_round_trip(self) -> None:
        formatted = format_size(1)

        assert formatted == '0.0 KB'

        reparsed = _parse_size(formatted)

        assert reparsed == 0
        assert format_size(reparsed) == '0 KB'

    def test_format_then_parse_round_trip_is_stable(self) -> None:
        originals = [512, 1_024, 50_000, 1_048_576, 1_073_741_824]

        for original in originals:
            formatted = format_size(original)
            reparsed = _parse_size(formatted)
            reformatted = format_size(reparsed)

            assert reformatted == formatted


class ParseSizeReturnTypeTests(BaseTestCase):
    def test_raw_bytes_returns_int(self) -> None:
        assert isinstance(_parse_size('1024'), int)

    def test_formatted_returns_int(self) -> None:
        assert isinstance(_parse_size('1.5 KB'), int)

    def test_float_raw_truncated_to_int(self) -> None:
        result = _parse_size('1024.9')

        assert isinstance(result, int)
        assert result == 1_024

    def test_none_return_is_none_not_zero(self) -> None:
        result = _parse_size('5 XB')

        assert result is None
        assert result != 0


class SizeMultipliersTests(BaseTestCase):
    def test_kb_is_1024(self) -> None:
        assert SIZE_MULTIPLIERS['KB'] == 1_024

    def test_mb_is_1024_squared(self) -> None:
        assert SIZE_MULTIPLIERS['MB'] == 1_024 ** 2

    def test_gb_is_1024_cubed(self) -> None:
        assert SIZE_MULTIPLIERS['GB'] == 1_024 ** 3

    def test_tb_is_1024_to_the_fourth(self) -> None:
        assert SIZE_MULTIPLIERS['TB'] == 1_024 ** 4

    def test_multipliers_match_utils_constants(self) -> None:
        assert SIZE_MULTIPLIERS['KB'] == SIZE_BYTES_PER_KB
        assert SIZE_MULTIPLIERS['MB'] == SIZE_BYTES_PER_MB
        assert SIZE_MULTIPLIERS['GB'] == SIZE_BYTES_PER_GB
        assert SIZE_MULTIPLIERS['TB'] == SIZE_BYTES_PER_TB

    def test_no_decimal_multipliers_present(self) -> None:
        assert 1_000 not in SIZE_MULTIPLIERS.values()
        assert 1_000_000 not in SIZE_MULTIPLIERS.values()
        assert 1_000_000_000 not in SIZE_MULTIPLIERS.values()


class ReverseThresholdsTests(BaseTestCase):
    def test_descending_order(self) -> None:
        values = [threshold for threshold, _ in REVERSE_THRESHOLDS]

        assert values == sorted(values, reverse=True)

    def test_thresholds_match_multipliers(self) -> None:
        threshold_map = {unit: val for val, unit in REVERSE_THRESHOLDS}

        for unit, multiplier in SIZE_MULTIPLIERS.items():
            assert threshold_map[unit] == multiplier

    def test_all_units_covered(self) -> None:
        threshold_units = {unit for _, unit in REVERSE_THRESHOLDS}

        assert threshold_units == set(SIZE_MULTIPLIERS.keys())

    def test_no_duplicate_units(self) -> None:
        units = [unit for _, unit in REVERSE_THRESHOLDS]

        assert len(units) == len(set(units))

    def test_no_duplicate_thresholds(self) -> None:
        values = [val for val, _ in REVERSE_THRESHOLDS]

        assert len(values) == len(set(values))
