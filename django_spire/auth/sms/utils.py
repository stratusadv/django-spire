from __future__ import annotations


def phone_number_normalize(phone_number: str) -> str | None:
    digits = ''.join(filter(str.isdigit, phone_number))

    if len(digits) == 10:
        return '+1' + digits

    if len(digits) == 11 and digits.startswith('1'):
        return '+' + digits

    return None
