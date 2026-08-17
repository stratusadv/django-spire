from __future__ import annotations

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.test import TestCase

from django_spire.auth.user.models import AuthUser
from django_spire.history.activity.context import activity_user, set_current_user
from django_spire.history.activity.models import Activity
from django_spire.history.models import HistoryEvent

from test_project.app.task.models import Task


class SignalActivityTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',  # noqa: S106
            first_name='Test',
            last_name='User',
        )
        self.task_content_type = ContentType.objects.get_for_model(Task)

    def tearDown(self) -> None:
        set_current_user(None)

    def task_activities(self, verb: str):
        return Activity.objects.filter(content_type=self.task_content_type, verb=verb)


class TestActivityUserAttribution(SignalActivityTestCase):
    def test_activity_user_attributes_save(self) -> None:
        with activity_user(self.user):
            task = Task.objects.create(name='One')

        activities = self.task_activities('created')

        assert activities.count() == 1
        assert activities.first().object_id == task.pk
        assert activities.first().user == self.user

    def test_activity_user_attributes_bulk_create(self) -> None:
        with activity_user(self.user):
            Task.objects.bulk_create([Task(name='One'), Task(name='Two')])

        assert self.task_activities('created').count() == 2

    def test_activity_user_attributes_delete(self) -> None:
        task = Task.objects.create(name='One')

        with activity_user(self.user):
            task.delete()

        assert self.task_activities('deleted').count() == 1

    def test_save_after_activity_user_block_logs_nothing(self) -> None:
        with activity_user(self.user):
            pass

        Task.objects.create(name='One')

        assert Activity.objects.count() == 0


class TestCreateSignalActivity(SignalActivityTestCase):
    def test_create_logs_created(self) -> None:
        set_current_user(self.user)

        task = Task.objects.create(name='One')

        activities = self.task_activities('created')

        assert activities.count() == 1
        activity = activities.first()
        assert activity.object_id == task.pk
        assert activity.user == self.user
        assert 'Test User created' in activity.information
        assert 'One' in activity.information

    def test_create_logs_exactly_one_activity(self) -> None:
        set_current_user(self.user)

        Task.objects.create(name='One')

        assert Activity.objects.count() == 1

    def test_save_new_instance_logs_created(self) -> None:
        set_current_user(self.user)

        task = Task(name='Unsaved')
        task.save()

        assert self.task_activities('created').count() == 1

    def test_create_without_user_logs_nothing(self) -> None:
        Task.objects.create(name='One')

        assert Activity.objects.count() == 0

    def test_get_or_create_logs_created_only_when_created(self) -> None:
        set_current_user(self.user)

        Task.objects.get_or_create(name='One')
        Task.objects.get_or_create(name='One')

        assert self.task_activities('created').count() == 1


class TestUpdateSignalActivity(SignalActivityTestCase):
    def test_save_existing_logs_updated(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.name = 'One Renamed'
        task.save()

        activities = self.task_activities('updated')

        assert activities.count() == 1
        activity = activities.first()
        assert activity.object_id == task.pk
        assert activity.user == self.user
        assert 'One Renamed' in activity.information

    def test_update_or_create_logs_updated_for_existing(self) -> None:
        Task.objects.create(name='One')

        set_current_user(self.user)

        Task.objects.update_or_create(name='One', defaults={'description': 'Changed'})

        assert self.task_activities('updated').count() == 1
        assert self.task_activities('created').count() == 0

    def test_set_deleted_logs_deleted(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.set_deleted()

        assert task.is_deleted is True
        assert self.task_activities('deleted').count() == 1
        assert self.task_activities('updated').count() == 0

    def test_set_deleted_twice_logs_deleted_once(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.set_deleted()
        task.set_deleted()

        assert self.task_activities('deleted').count() == 1
        assert self.task_activities('updated').count() == 1

    def test_save_without_user_logs_nothing(self) -> None:
        task = Task.objects.create(name='One')

        task.name = 'One Renamed'
        task.save()

        assert Activity.objects.count() == 0


class TestDeleteSignalActivity(SignalActivityTestCase):
    def test_instance_delete_logs_deleted(self) -> None:
        task = Task.objects.create(name='One')
        task_pk = task.pk

        set_current_user(self.user)

        task.delete()

        activities = self.task_activities('deleted')

        assert activities.count() == 1
        activity = activities.first()
        assert activity.object_id == task_pk
        assert activity.user == self.user
        assert 'Test User deleted' in activity.information

    def test_activity_survives_object_deletion(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.delete()

        assert Task.objects.count() == 0
        assert self.task_activities('deleted').count() == 1

    def test_queryset_delete_logs_deleted_per_row(self) -> None:
        task_1 = Task.objects.create(name='One')
        task_2 = Task.objects.create(name='Two')

        set_current_user(self.user)

        Task.objects.filter(pk__in=[task_1.pk, task_2.pk]).delete()

        activities = self.task_activities('deleted')

        assert activities.count() == 2
        assert {activity.object_id for activity in activities} == {task_1.pk, task_2.pk}

    def test_cascade_delete_logs_children(self) -> None:
        parent = Task.objects.create(name='Parent')
        child = Task.objects.create(name='Child', parent=parent)
        parent_pk = parent.pk
        child_pk = child.pk

        set_current_user(self.user)

        parent.delete()

        activities = self.task_activities('deleted')

        assert activities.count() == 2
        assert {activity.object_id for activity in activities} == {parent_pk, child_pk}

    def test_delete_without_user_logs_nothing(self) -> None:
        task = Task.objects.create(name='One')

        task.delete()

        assert Activity.objects.count() == 0


class TestSelfDeleteSignalActivity(TestCase):
    def tearDown(self) -> None:
        set_current_user(None)

    def test_deleting_the_acting_user_does_not_log_or_raise(self) -> None:
        user = AuthUser.objects.create_user(
            username='doomed',
            password='testpass',  # noqa: S106
            first_name='Doomed',
            last_name='User',
        )
        user_pk = user.pk

        set_current_user(user)

        user.delete()

        assert AuthUser.objects.filter(pk=user_pk).count() == 0
        assert Activity.objects.filter(verb='deleted', object_id=user_pk).count() == 0

    def test_deleting_another_user_logs_deleted(self) -> None:
        actor = AuthUser.objects.create_user(
            username='actor',
            password='testpass',  # noqa: S106
            first_name='Acting',
            last_name='User',
        )
        target = AuthUser.objects.create_user(
            username='target',
            password='testpass',  # noqa: S106
            first_name='Target',
            last_name='User',
        )
        target_pk = target.pk

        set_current_user(actor)

        target.delete()

        activities = Activity.objects.filter(verb='deleted', object_id=target_pk)

        assert activities.count() == 1
        assert activities.first().user == actor


class TestSignalRegistrationScope(TestCase):
    def test_activity_models_have_save_and_delete_listeners(self) -> None:
        assert post_save.has_listeners(Task) is True
        assert post_delete.has_listeners(Task) is True
        assert post_save.has_listeners(AuthUser) is True

    def test_models_without_mixin_have_no_listeners(self) -> None:
        assert post_save.has_listeners(HistoryEvent) is False
        assert post_delete.has_listeners(HistoryEvent) is False
        assert post_delete.has_listeners(Activity) is False

    def test_m2m_through_models_of_activity_models_have_listeners(self) -> None:
        assert m2m_changed.has_listeners(User.groups.through) is True
