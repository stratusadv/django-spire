from __future__ import annotations

from django.test import TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.contrib.shortcuts import get_object_or_null_obj
from django_spire.history.activity.models import Activity
from django_spire.history.activity.utils import add_form_activity


class TestAddFormActivity(TestCase):
    def setUp(self) -> None:
        self.super_user = AuthUser.objects.create_superuser(
            username='superuser', first_name='Super', last_name='User'
        )

    def test_add_form_activity_created(self) -> None:
        pk = 0
        user = get_object_or_null_obj(AuthUser, pk=pk)
        user.username = 'newuser'
        user.first_name = 'New'
        user.last_name = 'User'
        user.save()

        add_form_activity(user, pk=pk, user=self.super_user)

        assert Activity.objects.count() == 1
        activity = Activity.objects.first()
        assert activity is not None
        assert activity.verb == 'created'
        assert 'created' in activity.information
        assert 'Super User' in activity.information
        assert 'Auth User' in activity.information

    def test_add_form_activity_updated(self) -> None:
        user = get_object_or_null_obj(AuthUser, pk=0)
        user.username = 'updateuser'
        user.first_name = 'Update'
        user.last_name = 'User'
        user.save()

        add_form_activity(user, pk=user.pk, user=self.super_user)

        assert Activity.objects.count() == 1
        activity = Activity.objects.first()
        assert activity is not None
        assert activity.verb == 'updated'
        assert 'updated' in activity.information
        assert 'Super User' in activity.information
        assert 'Auth User' in activity.information

    def test_add_form_activity_multiple_calls(self) -> None:
        pk = 0
        user_1 = get_object_or_null_obj(AuthUser, pk=pk)
        user_1.username = 'user1'
        user_1.first_name = 'First'
        user_1.last_name = 'User'
        user_1.save()

        user_2 = get_object_or_null_obj(AuthUser, pk=pk)
        user_2.username = 'user2'
        user_2.first_name = 'Second'
        user_2.last_name = 'User'
        user_2.save()

        add_form_activity(user_1, pk=pk, user=self.super_user)
        add_form_activity(user_2, pk=user_2.pk, user=self.super_user)

        assert Activity.objects.count() == 2
        activities = Activity.objects.all().order_by('pk')
        assert activities[0].verb == 'created'
        assert 'created' in activities[0].information
        assert activities[1].verb == 'updated'
        assert 'updated' in activities[1].information
