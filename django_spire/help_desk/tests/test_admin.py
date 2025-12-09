from __future__ import annotations

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.admin import HelpDeskTicketAdmin
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskTicketAdminTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.site = AdminSite()
        self.admin = HelpDeskTicketAdmin(HelpDeskTicket, self.site)
        self.factory = RequestFactory()
        self.ticket = create_test_helpdesk_ticket()

    def test_list_display(self):
        expected = ('pk', 'purpose', 'priority', 'status', 'created_by', 'created_datetime')
        assert self.admin.list_display == expected

    def test_list_filter(self):
        expected = ('priority', 'purpose', 'status', 'is_active', 'is_deleted')
        assert self.admin.list_filter == expected

    def test_ordering(self):
        assert self.admin.ordering == ('-created_datetime',)

    def test_raw_id_fields(self):
        assert self.admin.raw_id_fields == ('created_by',)

    def test_readonly_fields(self):
        expected = ('created_by', 'created_datetime', 'is_active', 'is_deleted')
        assert self.admin.readonly_fields == expected

    def test_search_fields(self):
        expected = ('description', 'created_by__username', 'created_by__email')
        assert self.admin.search_fields == expected
