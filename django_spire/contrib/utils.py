from __future__ import annotations

from django_spire.core.constants import TIME_UNITS_TO_SECONDS


def truncate_string(string: str, length: int) -> str:
    return string[:(length - 3)] + '...' if len(string) > length else string


def format_duration(
        amount: float,
        start_unit: str = 'second',
        min_unit: str = 'second',
        included_units: list[str] | None = None,
        is_short_form: bool = False,
) -> str:
    """
    Converts duration into a readable format. (ex. 1h 15m or 1 hour 15 minutes)
    """

    if not amount or amount == 0:
        return 'N/A'

    if start_unit not in TIME_UNITS_TO_SECONDS.keys():
        return 'N/A'

    amount = amount * TIME_UNITS_TO_SECONDS[start_unit]

    components = []

    for unit, divisor in TIME_UNITS_TO_SECONDS.items():
        if included_units and unit not in included_units:
            continue

        converted_amount, amount = divmod(int(amount), divisor)

        if converted_amount > 0:
            if is_short_form:
                duration = f'{converted_amount}{unit[0]}'
            else:
                pluralize = '' if converted_amount == 1 else 's'
                duration = f'{converted_amount} {unit}{pluralize}'

            components.append(duration)

        # Stop if we reach the defined minimum unit
        if unit == min_unit:
            break

    separator = ' ' if is_short_form else ', '
    return separator.join(components)
