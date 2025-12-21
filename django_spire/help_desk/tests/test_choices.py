from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.choices import (
    HelpDeskTicketPriorityChoices,
    HelpDeskTicketPurposeChoices,
    HelpDeskTicketStatusChoices,
)


class HelpDeskTicketPurposeChoicesTests(BaseTestCase):
    def test_app_value(self):
        assert HelpDeskTicketPurposeChoices.APP == 'app'

    def test_company_value(self):
        assert HelpDeskTicketPurposeChoices.COMPANY == 'comp'

    def test_choices_count(self):
        assert len(HelpDeskTicketPurposeChoices.choices) == 2


class HelpDeskTicketStatusChoicesTests(BaseTestCase):
    def test_ready_value(self):
        assert HelpDeskTicketStatusChoices.READY == 'read'

    def test_inprogress_value(self):
        assert HelpDeskTicketStatusChoices.INPROGRESS == 'prog'

    def test_done_value(self):
        assert HelpDeskTicketStatusChoices.DONE == 'done'

    def test_choices_count(self):
        assert len(HelpDeskTicketStatusChoices.choices) == 3


class HelpDeskTicketPriorityChoicesTests(BaseTestCase):
    def test_low_value(self):
        assert HelpDeskTicketPriorityChoices.LOW == 'low'

    def test_medium_value(self):
        assert HelpDeskTicketPriorityChoices.MEDIUM == 'med'

    def test_high_value(self):
        assert HelpDeskTicketPriorityChoices.HIGH == 'high'

    def test_urgent_value(self):
        assert HelpDeskTicketPriorityChoices.URGENT == 'urge'

    def test_choices_count(self):
        assert len(HelpDeskTicketPriorityChoices.choices) == 4
