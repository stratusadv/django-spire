from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from django_spire.contrib.help.templatetags.help import help_button


class TestHelpButton(TestCase):
    @patch('django_spire.contrib.help.templatetags.help.render_to_string')
    def test_generates_unique_help_id(self, mock_render: patch) -> None:
        mock_render.return_value = ''

        help_button('test_template.html')

        calls = mock_render.call_args_list
        help_id_1 = calls[0][0][1]['help_id']

        mock_render.reset_mock()

        help_button('test_template.html')

        calls = mock_render.call_args_list
        help_id_2 = calls[0][0][1]['help_id']

        assert help_id_1 != help_id_2

    @patch('django_spire.contrib.help.templatetags.help.render_to_string')
    def test_help_id_starts_with_help_prefix(self, mock_render: patch) -> None:
        mock_render.return_value = ''

        help_button('test_template.html')

        calls = mock_render.call_args_list
        context = calls[0][0][1]

        assert context['help_id'].startswith('help-')

    @patch('django_spire.contrib.help.templatetags.help.render_to_string')
    def test_help_title_defaults_to_none(self, mock_render: patch) -> None:
        mock_render.return_value = ''

        help_button('test_template.html')

        calls = mock_render.call_args_list
        button_context = calls[0][0][1]

        assert button_context['help_title'] is None

    @patch('django_spire.contrib.help.templatetags.help.render_to_string')
    def test_passes_help_title_to_button_template(self, mock_render: patch) -> None:
        mock_render.return_value = ''

        help_button('test_template.html', help_title='Test Title')

        calls = mock_render.call_args_list
        button_context = calls[0][0][1]

        assert button_context['help_title'] == 'Test Title'

    @patch('django_spire.contrib.help.templatetags.help.render_to_string')
    def test_passes_help_title_to_modal_template(self, mock_render: patch) -> None:
        mock_render.return_value = ''

        help_button('test_template.html', help_title='Test Title')

        calls = mock_render.call_args_list

        # Order: button (0), help_content (1), modal (2)
        modal_context = calls[2][0][1]

        assert modal_context['help_title'] == 'Test Title'

    @patch('django_spire.contrib.help.templatetags.help.render_to_string')
    def test_renders_button_and_modal_templates(self, mock_render: patch) -> None:
        mock_render.return_value = ''

        help_button('test_template.html')

        assert mock_render.call_count == 3

    @patch('django_spire.contrib.help.templatetags.help.render_to_string')
    def test_returns_concatenated_button_and_modal(self, mock_render: patch) -> None:
        # Order of calls: button, help_content, modal
        mock_render.side_effect = ['<button>', '<content>', '<modal>']

        result = help_button('test_template.html')

        assert '<button>' in result
        assert '<modal>' in result

    @patch('django_spire.contrib.help.templatetags.help.render_to_string')
    def test_renders_help_content_template(self, mock_render: patch) -> None:
        mock_render.return_value = '<content>'

        help_button('custom_help.html')

        template_names = [call[0][0] for call in mock_render.call_args_list]
        assert 'custom_help.html' in template_names
