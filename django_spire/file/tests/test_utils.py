from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.utils import format_size, parse_extension, parse_name, random_64_char_token


class Random64CharTokenTests(BaseTestCase):
    def test_returns_string(self) -> None:
        result = random_64_char_token()

        assert isinstance(result, str)

    def test_returns_64_characters(self) -> None:
        result = random_64_char_token()

        assert len(result) == 64

    def test_returns_hexadecimal(self) -> None:
        result = random_64_char_token()

        int(result, 16)

    def test_returns_unique_values(self) -> None:
        result1 = random_64_char_token()
        result2 = random_64_char_token()

        assert result1 != result2

    def test_returns_lowercase(self) -> None:
        result = random_64_char_token()

        assert result == result.lower()


class ParseNameTests(BaseTestCase):
    def test_simple_filename(self) -> None:
        assert parse_name('document.pdf') == 'document'

    def test_multiple_dots(self) -> None:
        assert parse_name('my.file.name.pdf') == 'my.file.name'

    def test_no_extension(self) -> None:
        assert parse_name('document') == 'document'

    def test_empty_string(self) -> None:
        assert parse_name('') == ''

    def test_dotfile(self) -> None:
        assert parse_name('.hidden') == '.hidden'

    def test_trailing_dot(self) -> None:
        assert parse_name('file.') == 'file'

    def test_path_traversal_dots(self) -> None:
        assert parse_name('../../etc/passwd.txt') == '../../etc/passwd'

    def test_forward_slashes_preserved(self) -> None:
        assert parse_name('path/to/file.txt') == 'path/to/file'

    def test_backslashes_preserved(self) -> None:
        assert parse_name('path\\to\\file.txt') == 'path\\to\\file'

    def test_null_byte_in_name(self) -> None:
        assert parse_name('file\x00.txt') == 'file\x00'

    def test_unicode_name(self) -> None:
        assert parse_name('документ.pdf') == 'документ'

    def test_whitespace_only_before_dot(self) -> None:
        assert parse_name('   .pdf') == '   '

    def test_double_extension(self) -> None:
        assert parse_name('archive.tar.gz') == 'archive.tar'

    def test_many_dots(self) -> None:
        assert parse_name('a.b.c.d.e.f') == 'a.b.c.d.e'


class ParseExtensionTests(BaseTestCase):
    def test_simple_extension(self) -> None:
        assert parse_extension('document.pdf') == 'pdf'

    def test_uppercase_extension(self) -> None:
        assert parse_extension('document.PDF') == 'pdf'

    def test_mixed_case_extension(self) -> None:
        assert parse_extension('document.PdF') == 'pdf'

    def test_multiple_dots(self) -> None:
        assert parse_extension('my.file.name.pdf') == 'pdf'

    def test_no_extension(self) -> None:
        assert parse_extension('document') == ''

    def test_empty_string(self) -> None:
        assert parse_extension('') == ''

    def test_dotfile(self) -> None:
        assert parse_extension('.hidden') == ''

    def test_double_extension_returns_last(self) -> None:
        assert parse_extension('archive.tar.gz') == 'gz'

    def test_trailing_dot(self) -> None:
        assert parse_extension('file.') == ''

    def test_only_dots(self) -> None:
        assert parse_extension('...') == ''

    def test_space_in_extension(self) -> None:
        assert parse_extension('file.p d f') == 'p d f'

    def test_unicode_extension(self) -> None:
        assert parse_extension('file.données') == 'données'

    def test_path_traversal_in_name(self) -> None:
        assert parse_extension('../../etc/passwd.txt') == 'txt'

    def test_null_byte_in_extension(self) -> None:
        assert parse_extension('file.tx\x00t') == 'tx\x00t'


class FormatSizeTests(BaseTestCase):
    def test_zero_bytes(self) -> None:
        assert format_size(0) == '0 KB'

    def test_negative_bytes(self) -> None:
        assert format_size(-1) == '0 KB'

    def test_kilobytes(self) -> None:
        result = format_size(1_024)

        assert 'KB' in result

    def test_megabytes(self) -> None:
        result = format_size(1_048_576)

        assert 'MB' in result

    def test_gigabytes(self) -> None:
        result = format_size(1_073_741_824)

        assert 'GB' in result

    def test_terabytes(self) -> None:
        result = format_size(1_099_511_627_776)

        assert 'TB' in result

    def test_small_file(self) -> None:
        assert format_size(512) == '0.5 KB'

    def test_one_megabyte(self) -> None:
        assert format_size(1_048_576) == '1.0 MB'

    def test_boundary_below_megabyte(self) -> None:
        assert 'KB' in format_size(1_048_575)

    def test_boundary_at_megabyte(self) -> None:
        assert 'MB' in format_size(1_048_576)

    def test_boundary_below_gigabyte(self) -> None:
        assert 'MB' in format_size(1_073_741_823)

    def test_boundary_at_gigabyte(self) -> None:
        assert 'GB' in format_size(1_073_741_824)

    def test_one_byte(self) -> None:
        assert format_size(1) == '0.0 KB'

    def test_ten_bytes(self) -> None:
        assert format_size(10) == '0.01 KB'

    def test_exact_one_kb(self) -> None:
        assert format_size(1_024) == '1.0 KB'

    def test_negative_large_value(self) -> None:
        assert format_size(-999_999) == '0 KB'

    def test_max_int(self) -> None:
        result = format_size(2**63)

        assert 'TB' in result

    def test_just_under_one_kb(self) -> None:
        result = format_size(1_023)

        assert 'KB' in result
        assert float(result.split()[0]) <= 1.0

    def test_large_kb_does_not_promote_to_mb(self) -> None:
        result = format_size(999 * 1_024)

        assert 'KB' in result
