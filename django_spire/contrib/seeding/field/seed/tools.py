from django_spire.contrib.seeding.exceptions import DjangoSpireSeederError


def resolve_ordered_index(seed_index: int, length: int, wrap: bool, item_name: str) -> int:
    if wrap:
        return seed_index % length

    if seed_index >= length:
        message = (
            f'Cannot seed index {seed_index}: only {length} {item_name} available. '
            f'Pass wrap=True to cycle through them instead.'
        )
        raise DjangoSpireSeederError(message)

    return seed_index
