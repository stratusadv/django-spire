from __future__ import annotations

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory

from django_spire.ai.sms.admin import SmsConversationAdmin
from django_spire.ai.sms.models import SmsConversation
from django_spire.core.tests.test_cases import BaseTestCase


class SmsConversationAdminTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.site = AdminSite()
        self.admin = SmsConversationAdmin(SmsConversation, self.site)
        self.request = RequestFactory().get('/')
        self.request.user = self.super_user

        self.conversation = SmsConversation.objects.create(
            phone_number='+15555550100',
            user=self.super_user,
        )

        self.conversation.add_message(body='first', is_inbound=True, twilio_sid='a')
        self.conversation.add_message(body='second', is_inbound=False, twilio_sid='b')

    def test_message_link_filters_on_a_real_field(self) -> None:
        conversation = self.admin.get_queryset(self.request).get(pk=self.conversation.pk)

        result = self.admin.view_sms_messages_link(conversation)

        assert 'conversation__id=' in result
        assert 'sms_conversation__id=' not in result

    def test_message_link_uses_the_annotated_count(self) -> None:
        conversation = self.admin.get_queryset(self.request).get(pk=self.conversation.pk)

        with self.assertNumQueries(0):
            result = self.admin.view_sms_messages_link(conversation)

        assert '2 Messages' in result

    def test_message_link_target_returns_the_filtered_rows(self) -> None:
        conversation = self.admin.get_queryset(self.request).get(pk=self.conversation.pk)

        link = self.admin.view_sms_messages_link(conversation)
        url = link.split('href="')[1].split('"')[0]

        response = self.client.get(url)

        assert response.status_code == 200
        assert response.context['cl'].result_count == 2
