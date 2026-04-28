from __future__ import annotations

import gzip
import io

from django_spire.contrib.sync.core.exceptions import DecompressionLimitError


def gzip_decompress(data: bytes, bytes_max: int) -> bytes:
    buffer = io.BytesIO(data)
    result = bytearray()

    with gzip.GzipFile(fileobj=buffer) as gzip_file:
        while True:
            chunk = gzip_file.read(65536)

            if not chunk:
                break

            result.extend(chunk)

            if len(result) > bytes_max:
                message = f'Decompressed data exceeds limit of {bytes_max} bytes'
                raise DecompressionLimitError(message)

    return bytes(result)
