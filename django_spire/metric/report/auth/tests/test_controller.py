from __future__ import annotations

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory

from django_spire.auth.user.tests.factories import create_user
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.metric.report.auth.controller import BaseReportAuthController
from django_spire.metric.report.models import ReportRun


class BaseReportAuthControllerTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        self.user = create_user(username='test_auth_user')
        self.request = self.factory.get('/')
        self.request.user = self.user

        content_type = ContentType.objects.get_for_model(ReportRun)

        self.view_permission = Permission.objects.get(
            codename='view_reportrun',
            content_type=content_type
        )
        self.add_permission = Permission.objects.get(
            codename='add_reportrun',
            content_type=content_type
        )
        self.change_permission = Permission.objects.get(
            codename='change_reportrun',
            content_type=content_type
        )
        self.delete_permission = Permission.objects.get(
            codename='delete_reportrun',
            content_type=content_type
        )

    def _refresh_user_and_request(self):
        self.user = type(self.user).objects.get(pk=self.user.pk)
        self.request.user = self.user

    def test_can_view_without_permission(self):
        controller = BaseReportAuthController(self.request)
        assert controller.can_view() is False

    def test_can_view_with_permission(self):
        self.user.user_permissions.add(self.view_permission)
        self._refresh_user_and_request()

        controller = BaseReportAuthController(self.request)
        assert controller.can_view() is True

    def test_can_add_without_permission(self):
        controller = BaseReportAuthController(self.request)
        assert controller.can_add() is False

    def test_can_add_with_permission(self):
        self.user.user_permissions.add(self.add_permission)
        self._refresh_user_and_request()

        controller = BaseReportAuthController(self.request)
        assert controller.can_add() is True

    def test_can_change_without_permission(self):
        controller = BaseReportAuthController(self.request)
        assert controller.can_change() is False

    def test_can_change_with_permission(self):
        self.user.user_permissions.add(self.change_permission)
        self._refresh_user_and_request()

        controller = BaseReportAuthController(self.request)
        assert controller.can_change() is True

    def test_can_delete_without_permission(self):
        controller = BaseReportAuthController(self.request)
        assert controller.can_delete() is False

    def test_can_delete_with_permission(self):
        self.user.user_permissions.add(self.delete_permission)
        self._refresh_user_and_request()

        controller = BaseReportAuthController(self.request)
        assert controller.can_delete() is True