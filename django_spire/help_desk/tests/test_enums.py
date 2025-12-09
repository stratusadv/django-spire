from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.enums import TicketEventType


class TicketEventTypeTests(BaseTestCase):
    def test_new_value(self):
        assert TicketEventType.NEW.value == 'new'

    def test_update_value(self):
        assert TicketEventType.UPDATE.value == 'update'

    def test_comment_value(self):
        assert TicketEventType.COMMENT.value == 'comment'

    def test_enum_members_count(self):
        assert len(TicketEventType) == 3
