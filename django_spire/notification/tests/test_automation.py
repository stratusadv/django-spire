from __future__ import annotations

from unittest.mock import MagicMock, patch

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.automations import process_notifications


class NotificationAutomationsTests(BaseTestCase):
    @patch('django_spire.notification.automations.NotificationManager')
    def test_process_notifications_calls_manager(self, mock_manager_class: MagicMock):
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        result = process_notifications()

        mock_manager.process_ready_notifications.assert_called_once()
        assert result == 'Successfully Completed'
