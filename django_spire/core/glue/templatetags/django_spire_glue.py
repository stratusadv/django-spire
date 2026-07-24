from django import template

register = template.Library()


@register.filter
def glue_field_value_path(value: str) -> str:
    """Return the primitive field path."""
    return value.replace('.$fields.', '.')


@register.filter
def glue_field_metadata_path(value: str) -> str:
    """Return the rich $fields path."""
    if '.$fields.' in value:
        return value

    owner, field_name = value.rsplit('.', 1)
    return f'{owner}.$fields.{field_name}'
