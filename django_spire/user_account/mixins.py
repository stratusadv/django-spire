from django_spire.options.mixins import OptionsModelMixin
from django_spire.options.options import (
    Option,
    Options,
    OptionSection
)


DEFAULT_USER_OPTIONS = Options(sections=[
    OptionSection(
        name='notification',
        options=[
            Option('email', True),
        ]
    ),
    OptionSection(
        name='system',
        options=[
            Option('timezone', 'America/Edmonton'),
        ]
    ),
])


CANADA_TIMEZONES = (
    ('Vancouver', 'Pacific Time'),
    ('Edmonton', 'Mountain Time'),
    ('Winnipeg', 'Central Time'),
    ('Toronto', 'Eastern Time'),
    ('Halifax', 'Atlantic Time'),
    ('St_Johns', 'Newfoundland Time'),
)


class UserOptionsModelMixin(OptionsModelMixin):
    _default_options = DEFAULT_USER_OPTIONS

    class Meta:
        abstract = True
