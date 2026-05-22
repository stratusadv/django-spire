from __future__ import annotations

from test_project.apps.sync.config import TABLET_COUNT_DEFAULT


class _Context:
    database_name: str = 'tablet_1'
    tablet_count: int = TABLET_COUNT_DEFAULT


_context = _Context()


def get_current_database() -> str:
    return _context.database_name


def get_tablet_count() -> int:
    return _context.tablet_count


def set_tablet_count(count: int) -> None:
    _context.tablet_count = count


def switch_database(database_name: str) -> None:
    _context.database_name = database_name
