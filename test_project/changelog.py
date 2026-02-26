from datetime import date

from django_spire.contrib.changelog import Change, ChangelogEntry, ChangeLogTypeEnum


changelog = [
    ChangelogEntry(
        version='0.0.2',
        changes=[
            Change(
                app='test_project',
                description='Fixed a not cool bug!'
            ),
        ],
        date=date(2026, 2, 3),
        type=ChangeLogTypeEnum.BUG_FIX
    ),
    ChangelogEntry(
        version='0.0.1',
        changes=[
            Change(
                app='test_project',
                description='Added a cool feature!'
            ),
        ],
        date=date(2026, 2, 2),
        type=ChangeLogTypeEnum.FEATURE
    ),
    ChangelogEntry(
        version='0.0.0',
        changes=[
            Change(
                app='test_project',
                description='Made a cool change!'
            ),
        ],
        date=date(2026, 2, 1),
        type=ChangeLogTypeEnum.CHANGE
    ),
]
