from __future__ import annotations

from django.test import TestCase

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.group.services.services import AuthGroupService
from django_spire.auth.user.models import AuthUser
from django_spire.history.activity.context import activity_user, set_current_user
from django_spire.history.activity.models import Activity


class TestAuthGroupServiceActivity(TestCase):
    def setUp(self) -> None:
        self.actor = AuthUser.objects.create_user(
            username='serviceactor',
            first_name='Service',
            last_name='Actor',
        )

    def tearDown(self) -> None:
        set_current_user(None)

    def test_save_model_obj_attributes_activity_to_ambient_user(self) -> None:
        with activity_user(self.actor):
            group, _created = AuthGroupService(AuthGroup()).save_model_obj(name='Editors')

        activities = Activity.objects.filter(verb='created')

        assert activities.count() == 1
        assert activities.first().user == self.actor
        assert activities.first().object_id == group.pk

    def test_save_model_obj_without_ambient_user_logs_nothing(self) -> None:
        AuthGroupService(AuthGroup()).save_model_obj(name='Editors')

        assert Activity.objects.filter(verb='created').count() == 0
