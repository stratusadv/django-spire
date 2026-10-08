from __future__ import annotations

from typing import Any

from test_project.app.comment.models import CommentExample


def create_test_comment_example(**kwargs: Any) -> CommentExample:
    defaults = {
        'name': 'Quarterly Planning Notes',
        'description': 'Discussion thread for the quarterly planning session.',
    }

    defaults.update(kwargs)

    return CommentExample.objects.create(**defaults)
