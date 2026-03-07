from django import template

from django_spire.core.constants import TIME_UNITS_TO_SECONDS

register = template.Library()

@register.filter
def humanize_duration_simple(amount: float, start_unit: str = 'second') -> str:
    if not amount or amount == 0:
        return 'N/A'

    if start_unit not in TIME_UNITS_TO_SECONDS.keys():
        return 'N/A'

    amount = int(amount)

    if abs(amount) > 1:
        start_unit += 's'

    return f'{amount} {start_unit}'


@register.filter
def humanize_duration(amount: float, start_unit: str = 'second') -> str:
    if not amount or amount == 0:
        return 'N/A'

    if start_unit not in TIME_UNITS_TO_SECONDS.keys():
        return 'N/A'

    amount = amount * TIME_UNITS_TO_SECONDS[start_unit]

    components = []

    for unit, divisor in TIME_UNITS_TO_SECONDS.items():
        converted_amount, amount = divmod(int(amount), divisor)

        if converted_amount > 0:
            pluralize = '' if converted_amount == 1 else 's'
            duration = f'{converted_amount} {unit}{pluralize}'
            components.append(duration)

    return ', '.join(components)