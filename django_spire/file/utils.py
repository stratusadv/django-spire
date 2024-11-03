from __future__ import annotations

import binascii
import os


def random_64_char_token() -> str:
    return str(binascii.hexlify(os.urandom(32)).decode())
