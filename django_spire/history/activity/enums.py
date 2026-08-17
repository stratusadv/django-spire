from __future__ import annotations

from enum import StrEnum


class ActivityM2mAction(StrEnum):
    POST_ADD = 'post_add'
    POST_CLEAR = 'post_clear'
    POST_REMOVE = 'post_remove'
    PRE_ADD = 'pre_add'
    PRE_CLEAR = 'pre_clear'
    PRE_REMOVE = 'pre_remove'


class ActivityVerb(StrEnum):
    ADDED = 'added'
    CREATED = 'created'
    DELETED = 'deleted'
    REMOVED = 'removed'
    UPDATED = 'updated'
