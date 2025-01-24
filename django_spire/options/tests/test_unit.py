from __future__ import annotations

from django.test import RequestFactory

from django_spire.options.options import Options, OptionSection, Option
from django_spire.options.tests import factories
from django_spire.core.tests.test_cases import BaseTestCase


class OptionsUnitTestCase(BaseTestCase):
    pass

    # def test_option_get_settings(self):
    #     options = factories.create_test_options()
    #     self.assertEqual(options.get_setting('notification', 'push'), False)

    # def test_option_contains(self):
    #     options = factories.create_test_options()
    #     self.assertTrue('notification' in options)

    # def test_option_equal_true(self):
    #     self.assertEqual(factories.create_test_options(), factories.create_test_options())

    # def test_option_section_equal_false(self):
    #     options = factories.create_test_options()
    #     other_options = Options.load_dict({
    #         'General': {'volume': 10},
    #         'Notifications': {'email': True}
    #     })
    #     self.assertTrue(options != other_options)

    # def test_option_values_equal_false(self):
    #     options = Options.load_dict({
    #         'General': {'volume': 10, 'language': 'en'},
    #         'Notifications': {'email': True}
    #     })
    #     other_options = Options.load_dict({
    #         'General': {'volume': 10},
    #         'Notifications': {'email': True}
    #     })
    #     self.assertTrue(options != other_options)

    # def test_option_getitem(self):
    #     options = factories.create_test_options()
    #     self.assertEqual(type(options['notification']), OptionSection)
    #     self.assertEqual(type(options['notification']['push']), Option)
    #     self.assertEqual(options['notification']['push'].value, False)

    # def test_option_getitem_key_error(self):
    #     options = factories.create_test_options()
    #     with self.assertRaises(KeyError):
    #         options['invalid']

    # def test_option_load_dict(self):
    #     options = Options.load_dict(factories.create_test_options_dict())
    #     self.assertEqual(options.get_setting('notification', 'push'), False)
    #     self.assertTrue('notification' in options)

    # def test_option_update_setting(self):
    #     options = factories.create_test_options()
    #     options.update_setting('notification', 'push', True)
    #     self.assertEqual(options.get_setting('notification', 'push'), True)

    # def test_option_to_dict(self):
    #     options = factories.create_test_options()
    #     options_dict = factories.create_test_options_dict()
    #     self.assertEqual(options.to_dict(), options_dict)

    # def test_option_sync_options(self):
    #     original_options = Options.load_dict({
    #         'General': {'volume': 10},
    #         'Notifications': {'email': True}
    #     })
    #     new_structure = Options.load_dict({
    #         'General': {'volume': 5, 'brightness': 70},
    #         'Notifications': {'email': False, 'push': True},
    #         'Privacy': {'location': False}
    #     })
    #     original_options.sync_options(new_structure)

    #     # Check if the original value is preserved and new settings are added
    #     self.assertEqual(original_options.get_setting('General', 'volume'), 10)
    #     self.assertTrue('brightness' in original_options['General'])
    #     self.assertTrue('push' in original_options['Notifications'])
    #     self.assertTrue('Privacy' in original_options)


class OptionsSectionUnitTestCase(BaseTestCase):
    pass

    # def test_option_section_equal(self):
    #     self.assertEqual(factories.create_test_option_section(), factories.create_test_option_section())

    # def test_option_section_contains(self):
    #     section = factories.create_test_option_section()
    #     self.assertTrue('email' in section)

    # def test_option_section_getitem(self):
    #     section = factories.create_test_option_section()
    #     self.assertEqual(type(section['email']), Option)
    #     self.assertEqual(section['email'].value, True)

    # def test_option_section_getitem_key_error(self):
    #     section = factories.create_test_option_section()
    #     with self.assertRaises(KeyError):
    #         section['invalid']

    # def test_option_section_to_dict(self):
    #     section = OptionSection(
    #         name='notification',
    #         options=[
    #             Option('email', True),
    #             Option('push', False),
    #         ]
    #     )
    #     section_dict = {
    #         'email': True,
    #         'push': False
    #     }
    #     self.assertEqual(section.to_dict(), section_dict)


class OptionUnitTestCase(BaseTestCase):
    pass

    # def test_option_init(self):
    #     option = Option('email', True)
    #     self.assertEqual(option.key, 'email')
    #     self.assertEqual(option.value, True)


class OptionMixinUnitTestCase(BaseTestCase):
    pass

    # def test_mixin_get_option(self):
    #     mixin = factories.create_test_options_mixin()
    #     self.assertEqual(mixin.get_option('notification', 'email'), True)

    # def test_mixin_update_option(self):
    #     mixin = factories.create_test_options_mixin()
    #     mixin.update_option('notification', 'email', False, commit=False)
    #     self.assertEqual(mixin.get_option('notification', 'email'), False)
    #     self.assertEqual(mixin._options, mixin.options.to_dict())

    # def test_mixin_update_session(self):
    #     mixin = factories.create_test_options_mixin()
    #     request = RequestFactory()
    #     request.session = {}
    #     mixin.update_session(request)
    #     self.assertEqual(request.session['user_options'], mixin.options.to_dict())


