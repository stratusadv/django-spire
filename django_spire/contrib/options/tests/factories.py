from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.options.options import Options, Option, OptionSection
from django_spire.auth.user.tests.factories import create_user

if TYPE_CHECKING:
    from django_spire.contrib.options.mixins import OptionsModelMixin


def create_test_options() -> Options:
    # Test option to match test dict for testing
    return Options(sections=[
        OptionSection(
            name='notification',
            options=[
                Option('email', True),
                Option('push', False),
            ]
        ),
        OptionSection(
            name='system',
            options=[
                Option('timezone', 'America/Edmonton'),
            ]
        ),
    ])


def create_test_options_dict() -> dict:
    return {
        'notification': {
            'email': True,
            'push': False
        },
        'system': {
            'timezone': 'America/Edmonton'
        }
    }


def create_test_option_section() -> OptionSection:
    return OptionSection(
        name='notification',
        options=[
            Option('email', True),
            Option('push', False),
        ]
    )


def create_test_option() -> Option:
    return Option('email', True)


def create_test_options_mixin() -> OptionsModelMixin:
    user = create_user('Joe', 'goatery_99')
    profile = user.profile
    profile._default_options = create_test_options()
    profile.options = create_test_options()
    profile._options = profile.options.to_dict()
    return profile

