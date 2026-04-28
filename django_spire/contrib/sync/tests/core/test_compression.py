from __future__ import annotations

import gzip

import pytest

from django_spire.contrib.sync.core.compression import gzip_decompress
from django_spire.contrib.sync.core.exceptions import DecompressionLimitError


def test_decompresses_valid_gzip() -> None:
    payload = b'hello world'
    compressed = gzip.compress(payload)

    result = gzip_decompress(compressed, bytes_max=1024)

    assert result == payload


def test_round_trip_binary_data() -> None:
    payload = bytes(range(256)) * 10
    compressed = gzip.compress(payload)

    result = gzip_decompress(compressed, bytes_max=len(payload) + 1)

    assert result == payload


def test_rejects_exceeding_limit() -> None:
    payload = b'x' * 10_000
    compressed = gzip.compress(payload)

    with pytest.raises(DecompressionLimitError, match='exceeds limit'):
        gzip_decompress(compressed, bytes_max=100)


def test_limit_exactly_at_boundary() -> None:
    payload = b'x' * 1000
    compressed = gzip.compress(payload)

    result = gzip_decompress(compressed, bytes_max=1000)

    assert result == payload


def test_limit_one_byte_over_raises() -> None:
    payload = b'x' * 1001
    compressed = gzip.compress(payload)

    with pytest.raises(DecompressionLimitError):
        gzip_decompress(compressed, bytes_max=1000)


def test_empty_payload() -> None:
    compressed = gzip.compress(b'')

    result = gzip_decompress(compressed, bytes_max=1024)

    assert result == b''


def test_invalid_gzip_raises() -> None:
    with pytest.raises(Exception):
        gzip_decompress(b'not-gzip-data', bytes_max=1024)


def test_truncated_gzip_raises() -> None:
    payload = b'hello world'
    compressed = gzip.compress(payload)

    with pytest.raises(Exception):
        gzip_decompress(compressed[:5], bytes_max=1024)


def test_large_payload_under_limit() -> None:
    payload = b'A' * 100_000
    compressed = gzip.compress(payload)

    result = gzip_decompress(compressed, bytes_max=100_001)

    assert result == payload


def test_high_compression_ratio_bomb() -> None:
    payload = b'\x00' * 1_000_000
    compressed = gzip.compress(payload)

    assert len(compressed) < 2000

    with pytest.raises(DecompressionLimitError):
        gzip_decompress(compressed, bytes_max=10_000)
