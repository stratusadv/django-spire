from __future__ import annotations

from django_glue.enums import MessageLevel
from django_glue.message import GlueMessage
from urllib3 import HTTPResponse

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.choices import (
    HelpDeskTicketPriorityChoices,
    HelpDeskTicketPurposeChoices,
    HelpDeskTicketStatusChoices,
)
from django_spire.help_desk.forms import HelpDeskTicketModelForm
from django_spire.help_desk.tests.factories import create_test_helpdesk_ticket


class HelpDeskTicketModelFormTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.ticket = create_test_helpdesk_ticket()

    def test_valid_form(self):
        form_data = {
            'purpose': HelpDeskTicketPurposeChoices.APP,
            'priority': HelpDeskTicketPriorityChoices.LOW,
            'status': HelpDeskTicketStatusChoices.READY,
            'description': 'Test description',
        }

        form = HelpDeskTicketModelForm(data=form_data)
        request = HTTPResponse()
        request.user = self.super_user
        response = form.save_model_obj(request)

        assert response.status == 200
        assert form.is_valid()

    def test_invalid_form_missing_purpose(self):
        form_data = {
            'priority': HelpDeskTicketPriorityChoices.LOW,
            'description': 'Test description',
        }
        form = HelpDeskTicketModelForm(data=form_data)
        assert not form.is_valid()
        assert 'purpose' in form.errors

    def test_invalid_form_missing_priority(self):
        form_data = {'purpose': HelpDeskTicketPurposeChoices.APP, 'description': 'Test description'}
        form = HelpDeskTicketModelForm(data=form_data)
        assert not form.is_valid()
        assert 'priority' in form.errors

    def test_invalid_form_missing_description(self):
        form_data = {
            'purpose': HelpDeskTicketPurposeChoices.APP,
            'priority': HelpDeskTicketPriorityChoices.LOW,
        }
        form = HelpDeskTicketModelForm(data=form_data)
        assert not form.is_valid()
        assert 'description' in form.errors

    def test_excludes_created_by(self):
        assert 'created_by' not in HelpDeskTicketModelForm().fields

    def test_invalid_form_missing_status(self):
        form_data = {
            'purpose': HelpDeskTicketPurposeChoices.APP,
            'priority': HelpDeskTicketPriorityChoices.LOW,
            'description': 'Test description',
        }
        form = HelpDeskTicketModelForm(data=form_data, instance=self.ticket)
        assert not form.is_valid()
        assert 'status' in form.errors

    def test_invalid_form_short_description(self):
        form_data = {
            'purpose': HelpDeskTicketPurposeChoices.APP,
            'priority': HelpDeskTicketPriorityChoices.LOW,
            'status': HelpDeskTicketStatusChoices.READY,
            'description': 'Test',
        }

        form = HelpDeskTicketModelForm(data=form_data)
        request = HTTPResponse()
        request.user = self.super_user
        response = form.save_model_obj(request)

        assert response.status == 200
        assert response.messages == [
            GlueMessage(
                level=MessageLevel.WARNING,
                message='Your description is not long enough ... but I do care!',
            )
        ]
