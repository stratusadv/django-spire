from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.choices import (
    HelpDeskTicketPriorityChoices,
    HelpDeskTicketPurposeChoices,
    HelpDeskTicketStatusChoices,
)
from django_spire.help_desk.forms import (
    HelpDeskTicketCreateForm,
    HelpDeskTicketUpdateForm,
)
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskTicketCreateFormTests(BaseTestCase):
    def test_valid_form(self):
        form_data = {
            'purpose': HelpDeskTicketPurposeChoices.APP,
            'priority': HelpDeskTicketPriorityChoices.LOW,
            'description': 'Test description',
        }
        form = HelpDeskTicketCreateForm(data=form_data)
        assert form.is_valid()

    def test_invalid_form_missing_purpose(self):
        form_data = {
            'priority': HelpDeskTicketPriorityChoices.LOW,
            'description': 'Test description',
        }
        form = HelpDeskTicketCreateForm(data=form_data)
        assert not form.is_valid()
        assert 'purpose' in form.errors

    def test_invalid_form_missing_priority(self):
        form_data = {
            'purpose': HelpDeskTicketPurposeChoices.APP,
            'description': 'Test description',
        }
        form = HelpDeskTicketCreateForm(data=form_data)
        assert not form.is_valid()
        assert 'priority' in form.errors

    def test_invalid_form_missing_description(self):
        form_data = {
            'purpose': HelpDeskTicketPurposeChoices.APP,
            'priority': HelpDeskTicketPriorityChoices.LOW,
        }
        form = HelpDeskTicketCreateForm(data=form_data)
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_excludes_created_by(self):
        assert 'created_by' not in HelpDeskTicketCreateForm().fields

    def test_excludes_status(self):
        assert 'status' not in HelpDeskTicketCreateForm().fields


class HelpDeskTicketUpdateFormTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.ticket = create_test_helpdesk_ticket()

    def test_valid_form(self):
        form_data = {
            'purpose': HelpDeskTicketPurposeChoices.COMPANY,
            'priority': HelpDeskTicketPriorityChoices.HIGH,
            'status': HelpDeskTicketStatusChoices.INPROGRESS,
            'description': 'Updated description',
        }
        form = HelpDeskTicketUpdateForm(data=form_data, instance=self.ticket)
        assert form.is_valid()

    def test_includes_status(self):
        assert 'status' in HelpDeskTicketUpdateForm().fields

    def test_excludes_created_by(self):
        assert 'created_by' not in HelpDeskTicketUpdateForm().fields

    def test_invalid_form_missing_status(self):
        form_data = {
            'purpose': HelpDeskTicketPurposeChoices.APP,
            'priority': HelpDeskTicketPriorityChoices.LOW,
            'description': 'Test description',
        }
        form = HelpDeskTicketUpdateForm(data=form_data, instance=self.ticket)
        assert not form.is_valid()
        assert 'status' in form.errors
