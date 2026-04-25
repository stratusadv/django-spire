from __future__ import annotations

import gzip
import io

from django_spire.contrib.sync.core.exceptions import DecompressionLimitError


def safe_gzip_decompress(data: bytes, max_bytes: int) -> bytes:
    buffer = io.BytesIO(data)
    result = bytearray()

    with gzip.GzipFile(fileobj=buffer) as gzip_file:
        while True:
            chunk = gzip_file.read(65536)

            if not chunk:
                break

            result.extend(chunk)

            if len(result) > max_bytes:
                message = (
                    f'Decompressed data exceeds limit of '
                    f'{max_bytes} bytes'
                )

                raise DecompressionLimitError(message)

    return bytes(result)
