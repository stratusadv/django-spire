import pytest

from django.test import RequestFactory, TestCase
from unittest.mock import MagicMock

from django_spire.contrib.options.mixins import OptionsModelMixin
from django_spire.contrib.options.options import Option, Options, OptionSection
from django_spire.contrib.options.tests import factories


class TestOption(TestCase):
    def test_init(self) -> None:
        option = Option('email', True)

        assert option.key == 'email'
        assert option.value is True

    def test_value_can_be_string(self) -> None:
        option = Option('timezone', 'America/Edmonton')

        assert option.value == 'America/Edmonton'

    def test_value_can_be_int(self) -> None:
        option = Option('volume', 50)

        assert option.value == 50

    def test_value_can_be_bool(self) -> None:
        option = Option('enabled', False)

        assert option.value is False


class TestOptionSection(TestCase):
    def test_contains_existing_option(self) -> None:
        section = factories.create_test_option_section()

        assert 'email' in section

    def test_contains_missing_option(self) -> None:
        section = factories.create_test_option_section()

        assert 'invalid' not in section

    def test_equal(self) -> None:
        section1 = factories.create_test_option_section()
        section2 = factories.create_test_option_section()

        assert section1 == section2

    def test_getitem(self) -> None:
        section = factories.create_test_option_section()

        assert isinstance(section['email'], Option)
        assert section['email'].value is True

    def test_getitem_case_insensitive(self) -> None:
        section = factories.create_test_option_section()

        assert section['EMAIL'].value is True

    def test_getitem_key_error(self) -> None:
        section = factories.create_test_option_section()

        with pytest.raises(KeyError):
            section['invalid']

    def test_not_equal(self) -> None:
        section1 = factories.create_test_option_section()
        section2 = OptionSection(
            name='other',
            options=[Option('different', 'value')]
        )

        assert section1 != section2

    def test_to_dict(self) -> None:
        section = factories.create_test_option_section()
        expected = {'email': True, 'push': False}

        assert section.to_dict() == expected


class TestOptions(TestCase):
    def test_contains_existing_section(self) -> None:
        options = factories.create_test_options()

        assert 'notification' in options

    def test_contains_missing_section(self) -> None:
        options = factories.create_test_options()

        assert 'invalid' not in options

    def test_equal_same_structure(self) -> None:
        options1 = factories.create_test_options()
        options2 = factories.create_test_options()

        assert options1 == options2

    def test_equal_different_sections(self) -> None:
        options1 = factories.create_test_options()
        options2 = Options.load_dict({
            'General': {'volume': 10},
            'Notifications': {'email': True}
        })

        assert options1 != options2

    def test_equal_different_values_same_keys(self) -> None:
        options1 = Options.load_dict({
            'General': {'volume': 10, 'language': 'en'},
            'Notifications': {'email': True}
        })
        options2 = Options.load_dict({
            'General': {'volume': 10},
            'Notifications': {'email': True}
        })

        assert options1 != options2

    def test_get_setting(self) -> None:
        options = factories.create_test_options()

        assert options.get_setting('notification', 'push') is False

    def test_getitem(self) -> None:
        options = factories.create_test_options()

        assert isinstance(options['notification'], OptionSection)
        assert isinstance(options['notification']['push'], Option)
        assert options['notification']['push'].value is False

    def test_getitem_case_insensitive(self) -> None:
        options = factories.create_test_options()

        assert options['NOTIFICATION']['PUSH'].value is False

    def test_getitem_key_error(self) -> None:
        options = factories.create_test_options()

        with pytest.raises(KeyError):
            options['invalid']

    def test_load_dict(self) -> None:
        options_dict = factories.create_test_options_dict()
        options = Options.load_dict(options_dict)

        assert options.get_setting('notification', 'push') is False
        assert 'notification' in options

    def test_sync_options_adds_new_sections(self) -> None:
        original = Options.load_dict({
            'General': {'volume': 10},
        })
        new_structure = Options.load_dict({
            'General': {'volume': 5},
            'Privacy': {'location': False}
        })

        original.sync_options(new_structure)

        assert 'Privacy' in original

    def test_sync_options_adds_new_settings(self) -> None:
        original = Options.load_dict({
            'General': {'volume': 10},
        })
        new_structure = Options.load_dict({
            'General': {'volume': 5, 'brightness': 70},
        })

        original.sync_options(new_structure)

        assert 'brightness' in original['General']

    def test_sync_options_preserves_existing_values(self) -> None:
        original = Options.load_dict({
            'General': {'volume': 10},
        })
        new_structure = Options.load_dict({
            'General': {'volume': 5, 'brightness': 70},
        })

        original.sync_options(new_structure)

        assert original.get_setting('General', 'volume') == 10

    def test_to_dict(self) -> None:
        options = factories.create_test_options()
        expected = factories.create_test_options_dict()

        assert options.to_dict() == expected

    def test_update_setting(self) -> None:
        options = factories.create_test_options()

        options.update_setting('notification', 'push', True)

        assert options.get_setting('notification', 'push') is True


class TestOptionsModelMixin(TestCase):
    def test_get_option(self) -> None:
        mixin = MagicMock(spec=OptionsModelMixin)
        mixin._default_options = factories.create_test_options()
        mixin.options = factories.create_test_options()
        mixin._options = mixin.options.to_dict()

        result = OptionsModelMixin.get_option(mixin, 'notification', 'email')

        assert result is True

    def test_update_option(self) -> None:
        mixin = MagicMock(spec=OptionsModelMixin)
        mixin._default_options = factories.create_test_options()
        mixin.options = factories.create_test_options()
        mixin._options = mixin.options.to_dict()

        OptionsModelMixin.update_option(mixin, 'notification', 'email', False, commit=False)

        assert mixin.options.get_setting('notification', 'email') is False
        assert mixin._options == mixin.options.to_dict()

    def test_update_session(self) -> None:
        mixin = MagicMock(spec=OptionsModelMixin)
        mixin.options = factories.create_test_options()

        request = RequestFactory().get('/')
        request.session = {}

        OptionsModelMixin.update_session(mixin, request)

        assert request.session['user_options'] == mixin.options.to_dict()
