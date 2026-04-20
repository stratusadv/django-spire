from __future__ import annotations

import binascii
import os


def random_64_char_token() -> str:
    return binascii.hexlify(os.urandom(32)).decode()


def parse_name(filename: str) -> str:
    if not filename or '.' not in filename:
        return filename

    name, _ = filename.rsplit('.', 1)

    if not name:
        return filename

    return name


def parse_extension(filename: str) -> str:
    if not filename or '.' not in filename:
        return ''

    name, extension = filename.rsplit('.', 1)

    if not name:
        return ''

    return extension.lower()


def format_size(size_bytes: int) -> str:
    if size_bytes <= 0:
        return '0 KB'

    if size_bytes < 1_048_576:
        return f'{round(size_bytes / 1_024, 2)} KB'

    if size_bytes < 1_073_741_824:
        return f'{round(size_bytes / 1_048_576, 2)} MB'

    if size_bytes < 1_099_511_627_776:
        return f'{round(size_bytes / 1_073_741_824, 2)} GB'

    return f'{round(size_bytes / 1_099_511_627_776, 2)} TB'
