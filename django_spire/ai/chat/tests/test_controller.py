from __future__ import annotations

from django.contrib.auth.models import Permission, User
from django.test import RequestFactory

from django_spire.ai.chat.auth.controller import BaseAiChatAuthController
from django_spire.core.tests.test_cases import BaseTestCase


class BaseAiChatAuthControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.factory = RequestFactory()
        self.request = self.factory.get('/')
        self.request.user = self.super_user

    def test_can_delete_with_permission(self) -> None:
        permission = Permission.objects.get(codename='delete_chat')
        self.super_user.user_permissions.add(permission)

        self.super_user = type(self.super_user).objects.get(pk=self.super_user.pk)
        self.request.user = self.super_user

        controller = BaseAiChatAuthController(self.request)

        assert controller.can_delete() is True

    def test_can_delete_without_permission(self) -> None:
        regular_user = User.objects.create_user(
            username='regular_user',
            password='testpass123'  # noqa: S106
        )

        request = self.factory.get('/')
        request.user = regular_user

        controller = BaseAiChatAuthController(request)

        assert controller.can_delete() is False

    def test_controller_has_request(self) -> None:
        controller = BaseAiChatAuthController(self.request)

        assert controller.request == self.request
