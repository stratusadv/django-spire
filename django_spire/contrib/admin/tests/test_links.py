from __future__ import annotations

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_spire.contrib.admin.links import (
    admin_change_link,
    admin_change_url,
    admin_changelist_url,
    external_link,
    is_safe_link_url,
)
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class AdminChangeLinkTests(BaseTestCase):
    def test_registered_model_returns_anchor(self):
        ticket = create_test_helpdesk_ticket()

        result = admin_change_link(ticket)

        assert 'href=' in result
        assert str(ticket) in result

    def test_unregistered_model_degrades_to_text(self):
        content_type = ContentType.objects.get_for_model(HelpDeskTicket)

        result = admin_change_link(content_type)

        assert 'href=' not in result
        assert result == str(content_type)

    def test_none_returns_empty_text(self):
        assert admin_change_link(None) == '-'
        assert admin_change_link(None, empty_text='No Related Object') == 'No Related Object'

    def test_unsaved_instance_returns_no_url(self):
        assert admin_change_url(HelpDeskTicket()) is None


class AdminChangelistUrlTests(TestCase):
    def test_without_filters(self):
        url = admin_changelist_url(HelpDeskTicket)

        assert url.endswith('/')
        assert '?' not in url

    def test_with_filters(self):
        url = admin_changelist_url(HelpDeskTicket, priority='1')

        assert url.endswith('?priority=1')


class ExternalLinkTests(TestCase):
    def test_blocks_javascript_scheme(self):
        result = external_link('javascript:alert(1)', 'Link')

        assert 'href=' not in result
        assert result == 'javascript:alert(1)'

    def test_blocks_data_scheme(self):
        assert 'href=' not in external_link('data:text/html,<script>x</script>', 'Link')

    def test_blocks_protocol_relative_url(self):
        assert 'href=' not in external_link('//evil.example.com', 'Link')

    def test_empty_returns_empty_text(self):
        assert external_link('', 'Link', empty_text='No URL') == 'No URL'

    def test_relative_url_is_allowed(self):
        result = external_link('/notifications/1/', 'Link')

        assert 'href="/notifications/1/"' in result

    def test_sets_noopener_on_external_target(self):
        result = external_link('https://example.com', 'Link')

        assert 'rel="noopener noreferrer"' in result
        assert 'target="_blank"' in result

    def test_is_safe_link_url(self):
        assert is_safe_link_url('https://example.com')
        assert is_safe_link_url('http://example.com')
        assert is_safe_link_url('/relative/path')
        assert not is_safe_link_url('//example.com')
        assert not is_safe_link_url('javascript:alert(1)')
        assert not is_safe_link_url('ftp://example.com')
