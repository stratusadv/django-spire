from __future__ import annotations

from typing import Any

from test_project.app.history.models import HistoryExample


def create_test_history_example(**kwargs: Any) -> HistoryExample:
    defaults = {
        'name': 'Quarterly Review',
        'description': 'A record of what changed during the quarter.',
    }

    defaults.update(kwargs)

    return HistoryExample.objects.create(**defaults)
