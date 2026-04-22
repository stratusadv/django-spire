from __future__ import annotations

import binascii
import os

from pathlib import PurePosixPath

from django.core.signing import BadSignature, Signer


SIZE_BYTES_PER_KB = 1_024
SIZE_BYTES_PER_MB = 1_048_576
SIZE_BYTES_PER_GB = 1_073_741_824
SIZE_BYTES_PER_TB = 1_099_511_627_776


def random_64_char_token() -> str:
    return binascii.hexlify(os.urandom(32)).decode()


def parse_name(filename: str) -> str:
    if not filename:
        return ''

    return PurePosixPath(filename).stem


def parse_extension(filename: str) -> str:
    if not filename:
        return ''

    return PurePosixPath(filename).suffix.lstrip('.').lower()


def format_size(size_bytes: int) -> str:
    if size_bytes <= 0:
        return '0 KB'

    if size_bytes < SIZE_BYTES_PER_MB:
        return f'{round(size_bytes / SIZE_BYTES_PER_KB, 2)} KB'

    if size_bytes < SIZE_BYTES_PER_GB:
        return f'{round(size_bytes / SIZE_BYTES_PER_MB, 2)} MB'

    if size_bytes < SIZE_BYTES_PER_TB:
        return f'{round(size_bytes / SIZE_BYTES_PER_GB, 2)} GB'

    return f'{round(size_bytes / SIZE_BYTES_PER_TB, 2)} TB'


def sign_file_id(file_id: int) -> str:
    return Signer().sign(str(file_id))


def verify_file_token(file_id: int, token: str) -> bool:
    if not token:
        return False

    try:
        signed_id = Signer().unsign(token)
    except BadSignature:
        return False

    return str(file_id) == signed_id
