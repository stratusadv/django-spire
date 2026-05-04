from __future__ import annotations

from enum import StrEnum


class DashboardAction(StrEnum):
    SEED = 'seed'
    SYNC_ALL = 'sync_all'
    SYNC_CURRENT = 'sync_current'


class FieldOutcome(StrEnum):
    LOST = 'lost'
    MATCH = 'match'
    PULLED = 'pulled'
    PUSHED = 'pushed'
    WON = 'won'
    WON_CLOUD = 'won_cloud'
    WON_LOCAL = 'won_local'


class MergedOutcome(StrEnum):
    MATCH = 'match'
    PULLED = 'pulled'
    PUSHED = 'pushed'
    RESOLVED = 'resolved'


class RecordKind(StrEnum):
    CLOUD_ONLY = 'cloud_only'
    CONFLICT = 'conflict'
    MATCH = 'match'
    TABLET_ONLY = 'tablet_only'


class SeedScenario(StrEnum):
    LAND_SURVEY = 'land_survey'
    RANDOMIZED = 'randomized'


class SyncMode(StrEnum):
    ALL = 'all'
    CURRENT = 'current'


class SyncModelLabel(StrEnum):
    CLIENT = 'sync.Client'
    SITE = 'sync.Site'
    STAKE = 'sync.Stake'
    SURVEY_PLAN = 'sync.SurveyPlan'


class SyncStrategy(StrEnum):
    FIELD_OWNERSHIP = 'field_ownership'
    FIELD_TIMESTAMP_WINS = 'field_timestamp_wins'
    LOCAL_WINS = 'local_wins'
    REMOTE_WINS = 'remote_wins'


class VerificationStatus(StrEnum):
    CLOUD_ONLY = 'cloud_only'
    MATCH = 'match'
    MISMATCH = 'mismatch'
    TABLET_ONLY = 'tablet_only'


class WinnerSide(StrEnum):
    CLOUD = 'cloud'
    LOCAL = 'local'
    REMOTE = 'remote'


DEFAULT_STRATEGY: SyncStrategy = SyncStrategy.FIELD_TIMESTAMP_WINS

RESULT_CATEGORIES: tuple[str, ...] = (
    'applied', 'compatible', 'conflicts', 'created', 'deleted', 'skipped',
)

TRUNCATE_LIMIT: int = 40
