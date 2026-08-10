from __future__ import annotations


def phone_number_normalize(phone_number: str | None) -> str | None:
    if not phone_number:
        return None

    digits = ''.join(filter(str.isdigit, phone_number))

    if len(digits) == 10:
        return '+1' + digits

    if len(digits) == 11 and digits.startswith('1'):
        return '+' + digits

    return None


def phone_number_format_display(phone_number: str | None) -> str:
    normalized = phone_number_normalize(phone_number)

    if normalized is None:
        return phone_number or ''

    national = normalized[2:]

    if len(national) != 10:
        return phone_number or ''

    area = national[:3]
    prefix = national[3:6]
    line = national[6:]

    return f'({area}) {prefix}-{line}'
