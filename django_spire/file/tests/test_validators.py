from __future__ import annotations

import pytest

from django.core.exceptions import SuspiciousFileOperation

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.file.exceptions import FileValidationError
from django_spire.file.tests.factories import create_test_in_memory_uploaded_file
from django_spire.file.validators import FileValidator


class FileValidatorInitTests(BaseTestCase):
    def test_default_size_bytes_max(self) -> None:
        validator = FileValidator()

        assert validator.size_bytes_max == 10 * 1024 * 1024

    def test_default_allowed_extensions_is_none(self) -> None:
        validator = FileValidator()

        assert validator.allowed_extensions is None

    def test_default_blocked_extensions_contains_exe(self) -> None:
        validator = FileValidator()

        assert 'exe' in validator.blocked_extensions

    def test_default_validate_content_is_true(self) -> None:
        validator = FileValidator()

        assert validator.content_validation is True

    def test_zero_size_bytes_max_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match='size_bytes_max must be positive'):
            FileValidator(size_bytes_max=0)

    def test_negative_size_bytes_max_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match='size_bytes_max must be positive'):
            FileValidator(size_bytes_max=-1)

    def test_overlapping_extensions_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match='cannot be both allowed and blocked'):
            FileValidator(
                allowed_extensions=frozenset({'exe', 'pdf'}),
                blocked_extensions=frozenset({'exe'}),
            )

    def test_no_overlap_does_not_raise(self) -> None:
        validator = FileValidator(
            allowed_extensions=frozenset({'pdf', 'docx'}),
            blocked_extensions=frozenset({'exe'}),
        )

        assert validator.allowed_extensions == frozenset({'pdf', 'docx'})


class FileValidatorValidateTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.validator = FileValidator()

    def test_valid_file_does_not_raise(self) -> None:
        file = create_test_in_memory_uploaded_file()

        self.validator.validate(file)

    def test_none_file_raises(self) -> None:
        with pytest.raises(FileValidationError):
            self.validator.validate(None)

    def test_oversized_file_raises(self) -> None:
        validator = FileValidator(size_bytes_max=10)
        file = create_test_in_memory_uploaded_file(content=b'x' * 100)

        with pytest.raises(FileValidationError):
            validator.validate(file)

    def test_file_at_max_size_does_not_raise(self) -> None:
        validator = FileValidator(size_bytes_max=12)
        file = create_test_in_memory_uploaded_file(content=b'x' * 12)

        validator.validate(file)

    def test_blocked_extension_raises(self) -> None:
        file = create_test_in_memory_uploaded_file(name='malware', file_type='exe')

        with pytest.raises(FileValidationError):
            self.validator.validate(file)

    def test_allowed_extensions_rejects_unlisted(self) -> None:
        validator = FileValidator(
            allowed_extensions=frozenset({'pdf'}),
            blocked_extensions=frozenset(),
        )
        file = create_test_in_memory_uploaded_file(file_type='txt')

        with pytest.raises(FileValidationError):
            validator.validate(file)

    def test_allowed_extensions_accepts_listed(self) -> None:
        validator = FileValidator(
            allowed_extensions=frozenset({'pdf'}),
            blocked_extensions=frozenset(),
        )
        file = create_test_in_memory_uploaded_file(file_type='pdf')

        validator.validate(file)

    def test_unblocked_extension_does_not_raise(self) -> None:
        file = create_test_in_memory_uploaded_file(file_type='pdf')

        self.validator.validate(file)


class FileValidatorSizeNoneTests(BaseTestCase):
    def test_none_size_raises(self) -> None:
        validator = FileValidator(size_bytes_max=10)
        file = create_test_in_memory_uploaded_file(content=b'x' * 100)
        file.size = None

        with pytest.raises(FileValidationError, match='File size is unknown'):
            validator.validate(file)

    def test_zero_size_passes(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(content=b'')
        file.size = 0

        validator.validate(file)

    def test_file_one_byte_over_max_size_raises(self) -> None:
        validator = FileValidator(size_bytes_max=100)
        file = create_test_in_memory_uploaded_file(content=b'x' * 101)

        with pytest.raises(FileValidationError):
            validator.validate(file)


class FileValidatorDotfileTests(BaseTestCase):
    def test_dotfile_raises(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = '.gitignore'

        with pytest.raises(FileValidationError, match='File must have an extension'):
            validator.validate(file)

    def test_dotfile_with_allowed_extensions_rejects(self) -> None:
        validator = FileValidator(
            allowed_extensions=frozenset({'pdf'}),
            blocked_extensions=frozenset(),
        )
        file = create_test_in_memory_uploaded_file()
        file.name = '.gitignore'

        with pytest.raises(FileValidationError):
            validator.validate(file)


class FileValidatorExtensionCaseTests(BaseTestCase):
    def test_blocked_extension_uppercase(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'malware.EXE'

        with pytest.raises(FileValidationError):
            validator.validate(file)

    def test_blocked_extension_mixed_case(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'malware.ExE'

        with pytest.raises(FileValidationError):
            validator.validate(file)

    def test_allowed_extension_uppercase_accepted(self) -> None:
        validator = FileValidator(
            allowed_extensions=frozenset({'pdf'}),
            blocked_extensions=frozenset(),
        )
        file = create_test_in_memory_uploaded_file()
        file.name = 'document.PDF'

        validator.validate(file)


class FileValidatorDoubleExtensionTests(BaseTestCase):
    def test_exe_pdf_double_extension_passes_with_pdf_allowed(self) -> None:
        validator = FileValidator(
            allowed_extensions=frozenset({'pdf'}),
            blocked_extensions=frozenset(),
        )
        file = create_test_in_memory_uploaded_file()
        file.name = 'payload.exe.pdf'

        validator.validate(file)

    def test_pdf_exe_double_extension_blocked(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = 'document.pdf.exe'

        with pytest.raises(FileValidationError):
            validator.validate(file)


class FileValidatorEmptyNameTests(BaseTestCase):
    def test_empty_string_name_raises(self) -> None:
        file = create_test_in_memory_uploaded_file()

        with pytest.raises(SuspiciousFileOperation):
            file.name = ''

    def test_none_name_raises(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file()
        file.name = None

        with pytest.raises(FileValidationError):
            validator.validate(file)


class FileValidatorContentTests(BaseTestCase):
    def test_windows_pe_executable_rejected(self) -> None:
        validator = FileValidator(blocked_extensions=frozenset())
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'MZ' + b'\x00' * 100,
        )

        with pytest.raises(FileValidationError, match='executable binary'):
            validator.validate(file)

    def test_linux_elf_executable_rejected(self) -> None:
        validator = FileValidator(blocked_extensions=frozenset())
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'\x7fELF' + b'\x00' * 100,
        )

        with pytest.raises(FileValidationError, match='executable binary'):
            validator.validate(file)

    def test_macho_fat_binary_rejected(self) -> None:
        validator = FileValidator(blocked_extensions=frozenset())
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'\xca\xfe\xba\xbe' + b'\x00' * 100,
        )

        with pytest.raises(FileValidationError, match='executable binary'):
            validator.validate(file)

    def test_macho_64_rejected(self) -> None:
        validator = FileValidator(blocked_extensions=frozenset())
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'\xfe\xed\xfa\xcf' + b'\x00' * 100,
        )

        with pytest.raises(FileValidationError, match='executable binary'):
            validator.validate(file)

    def test_macho_reverse_rejected(self) -> None:
        validator = FileValidator(blocked_extensions=frozenset())
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'\xcf\xfa\xed\xfe' + b'\x00' * 100,
        )

        with pytest.raises(FileValidationError, match='executable binary'):
            validator.validate(file)

    def test_normal_pdf_content_passes(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'%PDF-1.4 fake pdf content',
        )

        validator.validate(file)

    def test_normal_png_content_passes(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(
            file_type='png',
            content=b'\x89PNG\r\n\x1a\n' + b'\x00' * 100,
        )

        validator.validate(file)

    def test_plain_text_content_passes(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(
            file_type='txt',
            content=b'just some text',
        )

        validator.validate(file)

    def test_empty_content_passes(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'',
        )
        file.size = 0

        validator.validate(file)

    def test_content_check_preserves_file_position(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(content=b'hello world')
        file.seek(5)

        validator.validate(file)

        assert file.tell() == 5

    def test_validate_content_false_skips_check(self) -> None:
        validator = FileValidator(
            blocked_extensions=frozenset(),
            content_validation=False,
        )
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'MZ' + b'\x00' * 100,
        )

        validator.validate(file)

    def test_pe_disguised_as_jpg_rejected(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(
            file_type='jpg',
            content=b'MZ\x90\x00' + b'\x00' * 100,
        )

        with pytest.raises(FileValidationError, match='executable binary'):
            validator.validate(file)

    def test_pe_disguised_as_docx_rejected(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(
            file_type='docx',
            content=b'MZ' + b'\x00' * 100,
        )

        with pytest.raises(FileValidationError, match='executable binary'):
            validator.validate(file)

    def test_partial_signature_not_rejected(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'M',
        )

        validator.validate(file)

    def test_signature_at_offset_not_rejected(self) -> None:
        validator = FileValidator()
        file = create_test_in_memory_uploaded_file(
            file_type='pdf',
            content=b'\x00\x00MZ' + b'\x00' * 100,
        )

        validator.validate(file)
