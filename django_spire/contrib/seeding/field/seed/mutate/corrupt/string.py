import random
from typing import Any, Callable


def get_methods(severity: str) -> dict[str, Callable]:
    if severity == 'mild':
        return _mild_methods
    if severity == 'moderate':
        return {**_mild_methods, **_moderate_methods}
    if severity == 'chaos':
        return {**_mild_methods, **_moderate_methods, **_chaos_methods}
    return _mild_methods


def _to_string(value: Any) -> str:
    if isinstance(value, str):
        return value
    return str(value)


def _corrupt_case(value: str) -> str:
    if not isinstance(value, str) or len(value) == 0:
        return str(value)
    if random.random() > 0.5:
        return value.swapcase()
    return value.upper()[:1].lower() + value[1:].upper()


def _truncate(value: str) -> str:
    if not isinstance(value, str) or len(value) == 0:
        return str(value)
    return value[: max(1, len(value) - 1)]


def _typo(value: str) -> str:
    if not isinstance(value, str) or len(value) < 2:
        return str(value)
    idx = random.randint(0, len(value) - 1)
    chars = list(value)
    chars[idx] = random.choice('abcdefghijklmnopqrstuvwxyz')
    return ''.join(chars)


def _swap_chars(value: str) -> str:
    if not isinstance(value, str) or len(value) < 3:
        return str(value)
    a, b = random.sample(range(len(value)), 2)
    chars = list(value)
    chars[a], chars[b] = chars[b], chars[a]
    return ''.join(chars)


def _insert_char(value: str) -> str:
    if not isinstance(value, str):
        return str(value)
    idx = random.randint(0, len(value))
    return value[:idx] + random.choice('abcdefghijklmnopqrstuvwxyz ') + value[idx:]


def _delete_char(value: str) -> str:
    if not isinstance(value, str) or len(value) < 2:
        return str(value)
    idx = random.randint(0, len(value) - 1)
    return value[:idx] + value[idx + 1 :]


def _inject_unicode(value: str) -> str:
    if not isinstance(value, str):
        return str(value)
    return value + random.choice(['\ufeff', '\u200b', '\u200c', '\u00a0'])


def _inject_sql_injection(value: str) -> str:
    if not isinstance(value, str):
        return str(value)
    return value + random.choice(["'; DROP TABLE--", '1=1--', 'OR 1=1'])


def _inject_xss_payload(value: str) -> str:
    if not isinstance(value, str):
        return str(value)
    return value + random.choice(['<script>alert(1)</script>', '><img src=x onerror=alert(1)>'])


def _inject_null_bytes(value: str) -> str:
    if not isinstance(value, str):
        return str(value)
    return value + random.choice(['\x00', '\x1a'])


def _scramble_chars(value: str) -> str:
    if not isinstance(value, str) or len(value) < 2:
        return str(value)
    chars = list(value)
    random.shuffle(chars)
    return ''.join(chars)


def _inject_newlines(value: str) -> str:
    if not isinstance(value, str):
        return str(value)
    return value + random.choice(['\n', '\r\n', '\t'])


_mild_methods: dict[str, Callable] = {
    '_corrupt_case': _corrupt_case,
    '_truncate': _truncate,
    '_typo': _typo,
}

_moderate_methods: dict[str, Callable] = {
    '_swap_chars': _swap_chars,
    '_insert_char': _insert_char,
    '_delete_char': _delete_char,
}

_chaos_methods: dict[str, Callable] = {
    '_inject_unicode': _inject_unicode,
    '_inject_sql_injection': _inject_sql_injection,
    '_inject_xss_payload': _inject_xss_payload,
    '_inject_null_bytes': _inject_null_bytes,
    '_scramble_chars': _scramble_chars,
    '_inject_newlines': _inject_newlines,
}
