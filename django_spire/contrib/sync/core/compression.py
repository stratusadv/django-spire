from __future__ import annotations

import gzip
import io

from django_spire.contrib.sync.core.exceptions import (
    DecompressionLimitError,
    InvalidParameterError,
)


_CHUNK_SIZE = 65536


def gzip_decompress(data: bytes, bytes_max: int) -> bytes:
    if bytes_max < 1:
        message = f'bytes_max must be >= 1, got {bytes_max}'
        raise InvalidParameterError(message)

    chunks_max = (bytes_max // _CHUNK_SIZE) + 2

    buffer = io.BytesIO(data)
    result = bytearray()

    with gzip.GzipFile(fileobj=buffer) as gzip_file:
        for _ in range(chunks_max):
            chunk = gzip_file.read(_CHUNK_SIZE)

            if not chunk:
                break

            result.extend(chunk)

            if len(result) > bytes_max:
                message = (
                    f'Decompressed data exceeds limit '
                    f'of {bytes_max} bytes'
                )

                raise DecompressionLimitError(message)
        else:
            message = (
                f'Decompression exceeded {chunks_max} chunks '
                f'without completing'
            )

            raise DecompressionLimitError(message)

    if len(result) > bytes_max:
        message = (
            f'Decompressed data exceeds limit '
            f'of {bytes_max} bytes'
        )

        raise DecompressionLimitError(message)

    return bytes(result)
