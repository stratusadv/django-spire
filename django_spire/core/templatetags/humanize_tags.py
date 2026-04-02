from django import template
from django_spire.contrib.utils import format_duration

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
def humanize_duration(amount: float, **kwargs) -> str:
    return format_duration(amount, **kwargs)

@register.filter
def humanize_duration_compact(amount: float, **kwargs) -> str:
    return format_duration(amount, is_short_form=True, **kwargs)
