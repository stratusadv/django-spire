from __future__ import annotations


TABLET_COUNT_DEFAULT = 3
TABLET_COUNT_MAX = 5


def get_active_sync_databases(count: int) -> list[str]:
    return [*get_active_tablet_databases(count), 'cloud']


def get_active_tablet_databases(count: int) -> list[str]:
    clamped = max(1, min(count, TABLET_COUNT_MAX))
    return [f'tablet_{i}' for i in range(1, clamped + 1)]


def get_all_sync_databases() -> list[str]:
    return get_active_sync_databases(TABLET_COUNT_MAX)
