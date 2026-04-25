from __future__ import annotations

from test_project.apps.sync.config import TABLET_COUNT_DEFAULT


class _Context:
    db: str = 'tablet_1'
    tablet_count: int = TABLET_COUNT_DEFAULT


_context = _Context()


def get_current_db() -> str:
    return _context.db


def get_tablet_count() -> int:
    return _context.tablet_count


def set_tablet_count(count: int) -> None:
    _context.tablet_count = count


def switch_db(db_name: str) -> None:
    _context.db = db_name
