from __future__ import annotations

from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.notification.app.models import AppNotification
from django_spire.notification.choices import NotificationTypeChoices
from django_spire.notification.email.models import EmailNotification
from django_spire.notification.maps import NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
from django_spire.notification.push.models import PushNotification
from django_spire.notification.sms.models import SmsNotification


class NotificationMapsTests(BaseTestCase):
    def test_map_contains_app(self):
        assert NotificationTypeChoices.APP in NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
        assert NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP[NotificationTypeChoices.APP] == AppNotification

    def test_map_contains_email(self):
        assert NotificationTypeChoices.EMAIL in NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
        assert NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP[NotificationTypeChoices.EMAIL] == EmailNotification

    def test_map_contains_push(self):
        assert NotificationTypeChoices.PUSH in NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
        assert NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP[NotificationTypeChoices.PUSH] == PushNotification

    def test_map_contains_sms(self):
        assert NotificationTypeChoices.SMS in NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
        assert NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP[NotificationTypeChoices.SMS] == SmsNotification

    def test_map_has_all_notification_types(self):
        for choice in NotificationTypeChoices:
            assert choice in NOTIFICATION_TYPE_CHOICE_TO_MODEL_MAP
