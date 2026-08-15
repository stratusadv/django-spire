from __future__ import annotations

import tempfile

from pathlib import Path

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.management import call_command
from django.test import TestCase

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser
from django_spire.comment.models import Comment
from django_spire.history.activity.context import set_current_user
from django_spire.history.activity.enums import ActivityM2mAction, ActivityVerb
from django_spire.history.activity.models import Activity
from django_spire.history.choices import HistoryEventChoices

from test_project.app.comment.models import CommentExample
from test_project.app.task.models import Task


class SignalEdgeTestCase(TestCase):
    def setUp(self) -> None:
        self.user = AuthUser.objects.create_user(
            username='edgeactor',
            first_name='Edge',
            last_name='Actor',
        )

    def tearDown(self) -> None:
        set_current_user(None)


class TestProxyModelActivity(SignalEdgeTestCase):
    def test_proxy_model_create_logs_activity(self) -> None:
        set_current_user(self.user)

        AuthUser.objects.create_user(username='proxytarget')

        assert Activity.objects.filter(verb='created').count() == 1

    def test_concrete_model_create_logs_nothing(self) -> None:
        set_current_user(self.user)

        User.objects.create_user(username='concretetarget')

        assert Activity.objects.filter(verb='created').count() == 0

    def test_proxy_activity_uses_the_concrete_content_type(self) -> None:
        set_current_user(self.user)

        target = AuthUser.objects.create_user(username='proxycontenttype')
        activity = Activity.objects.get(verb='created')

        assert activity.content_type == ContentType.objects.get_for_model(User)
        assert activity.object_id == target.pk

    def test_proxy_group_create_logs_one_activity(self) -> None:
        set_current_user(self.user)

        group = AuthGroup.objects.create(name='Editors')
        activity = Activity.objects.get(verb='created')

        assert Activity.objects.count() == 1
        assert activity.object_id == group.pk
        assert activity.content_type == ContentType.objects.get_for_model(AuthGroup)


class TestSaveVariantActivity(SignalEdgeTestCase):
    def test_save_with_update_fields_logs_updated(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.description = 'Changed'
        task.save(update_fields=['description'])

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_save_with_empty_update_fields_logs_nothing(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.description = 'Changed'
        task.save(update_fields=[])

        assert Activity.objects.count() == 0

    def test_force_insert_logs_created(self) -> None:
        set_current_user(self.user)

        task = Task(name='One')
        task.save(force_insert=True)

        assert Activity.objects.filter(verb='created').count() == 1

    def test_force_update_logs_updated(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.name = 'One Renamed'
        task.save(force_update=True)

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_deferred_instance_save_logs_updated_with_the_current_name(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        deferred_task = Task.objects.defer('description').get(pk=task.pk)
        deferred_task.name = 'One Renamed'
        deferred_task.save()

        activity = Activity.objects.get(verb='updated')

        assert 'One Renamed' in activity.information

    def test_only_pk_instance_save_logs_updated(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        minimal_task = Task.objects.only('id').get(pk=task.pk)
        minimal_task.save()

        activity = Activity.objects.get(verb='updated')

        assert 'One' in activity.information

    def test_explicit_primary_key_insert_logs_created(self) -> None:
        set_current_user(self.user)

        task = Task(pk=987654, name='One')
        task.save()

        activity = Activity.objects.get(verb='created')

        assert activity.object_id == 987654


class TestHistoryStateTransitionActivity(SignalEdgeTestCase):
    def test_set_inactive_logs_updated(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.set_inactive()

        assert Activity.objects.filter(verb='updated').count() == 1
        assert Activity.objects.filter(verb='deleted').count() == 0

    def test_set_active_logs_updated(self) -> None:
        task = Task.objects.create(name='One', is_active=False)

        set_current_user(self.user)

        task.set_active()

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_un_set_deleted_logs_updated(self) -> None:
        task = Task.objects.create(name='One', is_deleted=True)

        set_current_user(self.user)

        task.un_set_deleted()

        task.refresh_from_db()

        assert task.is_deleted is False
        assert Activity.objects.filter(verb='updated').count() == 1
        assert Activity.objects.filter(verb='deleted').count() == 0

    def test_set_deleted_writes_both_a_history_event_and_an_activity(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.set_deleted()

        history_events = task.history_events.filter(event=HistoryEventChoices.DELETED)

        assert history_events.count() == 1
        assert Activity.objects.filter(verb='deleted').count() == 1

    def test_set_deleted_then_un_set_deleted_then_set_deleted_logs_two_deletes(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.set_deleted()
        task.un_set_deleted()
        task.set_deleted()

        assert Activity.objects.filter(verb='deleted').count() == 2
        assert Activity.objects.filter(verb='updated').count() == 1


class TestActorIdentityActivity(SignalEdgeTestCase):
    def test_delete_of_a_row_sharing_the_actor_primary_key_still_logs(self) -> None:
        task = Task(pk=self.user.pk, name='Shared Primary Key')
        task.save()

        set_current_user(self.user)

        task.delete()

        activities = Activity.objects.filter(verb='deleted')

        assert activities.count() == 1
        assert activities.first().object_id == self.user.pk

    def test_inactive_actor_is_still_attributed(self) -> None:
        inactive_user = AuthUser.objects.create_user(
            username='inactiveactor',
            first_name='Inactive',
            last_name='Actor',
        )

        inactive_user.is_active = False
        inactive_user.save()

        set_current_user(inactive_user)

        task = Task.objects.create(name='One')
        activity = Activity.objects.get(verb='created', object_id=task.pk)

        assert activity.user == inactive_user

    def test_actor_without_a_name_falls_back_to_the_username(self) -> None:
        service_account = AuthUser.objects.create_user(username='serviceaccount')

        set_current_user(service_account)

        Task.objects.create(name='One')
        activity = Activity.objects.get(verb='created')

        assert activity.information.startswith('serviceaccount created')


class TestRawSaveActivity(SignalEdgeTestCase):
    def test_loaddata_creates_no_activity(self) -> None:
        set_current_user(self.user)

        task = Task.objects.create(name='One')
        Activity.objects.all().delete()

        fixture_json = serializers.serialize('json', [task])

        with tempfile.TemporaryDirectory() as directory:
            fixture_path = Path(directory) / 'activity_task_fixture.json'
            fixture_path.write_text(fixture_json)

            call_command('loaddata', str(fixture_path), verbosity=0)

        assert Task.objects.filter(pk=task.pk).exists()
        assert Activity.objects.count() == 0


class TestUnauditedWriteActivity(SignalEdgeTestCase):
    def test_direct_through_row_creation_logs_nothing(self) -> None:
        group = AuthGroup.objects.create(name='Editors')
        member = AuthUser.objects.create_user(username='directmember')

        set_current_user(self.user)

        through_model = User.groups.through
        through_model.objects.create(user_id=member.pk, group_id=group.pk)

        assert member.groups.count() == 1
        assert Activity.objects.filter(verb='added').count() == 0

    def test_activity_rows_are_not_themselves_audited(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.add_activity(user=self.user, verb='archived', information='Archived.')

        assert Activity.objects.count() == 1

    def test_cascade_delete_logs_only_the_audited_rows(self) -> None:
        example = CommentExample.objects.create(name='Example')
        example.add_comment(user=self.user, information='hello')

        set_current_user(self.user)

        example.delete()

        assert Comment.objects.count() == 0
        assert Activity.objects.filter(verb='deleted').count() == 1


class TestHardDeleteActivityLifetime(SignalEdgeTestCase):
    def test_hard_delete_discards_prior_activity_rows(self) -> None:
        set_current_user(self.user)

        task = Task.objects.create(name='One')
        task.name = 'One Renamed'
        task.save()

        assert Activity.objects.count() == 2

        task.delete()

        verbs = list(Activity.objects.values_list('verb', flat=True))

        assert verbs == ['deleted']

    def test_queryset_hard_delete_discards_prior_activity_rows(self) -> None:
        set_current_user(self.user)

        task = Task.objects.create(name='One')
        Task.objects.filter(pk=task.pk).delete()

        verbs = list(Activity.objects.values_list('verb', flat=True))

        assert verbs == ['deleted']

    def test_soft_delete_keeps_prior_activity_rows(self) -> None:
        set_current_user(self.user)

        task = Task.objects.create(name='One')
        task.set_deleted()

        verbs = sorted(Activity.objects.values_list('verb', flat=True))

        assert verbs == ['created', 'deleted']


class TestActivityInformationFormat(SignalEdgeTestCase):
    def test_created_information_is_a_full_sentence(self) -> None:
        set_current_user(self.user)

        Task.objects.create(name='One')
        activity = Activity.objects.get(verb='created')

        assert activity.information == 'Edge Actor created Task "One".'

    def test_updated_information_is_a_full_sentence(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.name = 'One Renamed'
        task.save()

        activity = Activity.objects.get(verb='updated')

        assert activity.information == 'Edge Actor updated Task "One Renamed".'

    def test_deleted_information_is_a_full_sentence(self) -> None:
        task = Task.objects.create(name='One')

        set_current_user(self.user)

        task.delete()

        activity = Activity.objects.get(verb='deleted')

        assert activity.information == 'Edge Actor deleted Task "One".'

    def test_bulk_information_matches_the_single_row_format(self) -> None:
        set_current_user(self.user)

        Task.objects.bulk_create([Task(name='One')])
        activity = Activity.objects.get(verb='created')

        assert activity.information == 'Edge Actor created Task "One".'


class TestM2mNameCapActivity(SignalEdgeTestCase):
    def created_groups(self, count: int) -> list[AuthGroup]:
        groups = [AuthGroup(name=f'Group {index:02d}') for index in range(count)]
        AuthGroup.objects.bulk_create(groups)

        return groups

    def test_add_at_the_named_cap_names_every_row(self) -> None:
        groups = self.created_groups(10)

        set_current_user(self.user)

        self.user.groups.add(*groups)

        activity = Activity.objects.get(verb='added')

        assert 'added 10 groups to' in activity.information
        assert 'Group 09' in activity.information
        assert 'more)' not in activity.information

    def test_add_over_the_named_cap_truncates_the_names(self) -> None:
        groups = self.created_groups(12)

        set_current_user(self.user)

        self.user.groups.add(*groups)

        activity = Activity.objects.get(verb='added')

        assert 'added 12 groups to' in activity.information
        assert 'Group 00' in activity.information
        assert 'and 2 more' in activity.information

    def test_remove_over_the_named_cap_truncates_the_names(self) -> None:
        groups = self.created_groups(12)
        self.user.groups.add(*groups)

        set_current_user(self.user)

        self.user.groups.remove(*groups)

        activity = Activity.objects.get(verb='removed')

        assert 'removed 12 groups from' in activity.information
        assert 'and 2 more' in activity.information

    def test_single_row_uses_the_singular_verbose_name(self) -> None:
        groups = self.created_groups(1)

        set_current_user(self.user)

        self.user.groups.add(*groups)

        activity = Activity.objects.get(verb='added')

        assert 'added 1 group to' in activity.information


class TestActivityEnums(TestCase):
    def test_verb_values_are_stable(self) -> None:
        assert ActivityVerb.ADDED == 'added'
        assert ActivityVerb.CREATED == 'created'
        assert ActivityVerb.DELETED == 'deleted'
        assert ActivityVerb.REMOVED == 'removed'
        assert ActivityVerb.UPDATED == 'updated'

    def test_m2m_action_values_match_django_signal_actions(self) -> None:
        assert ActivityM2mAction.POST_ADD == 'post_add'
        assert ActivityM2mAction.POST_CLEAR == 'post_clear'
        assert ActivityM2mAction.POST_REMOVE == 'post_remove'
        assert ActivityM2mAction.PRE_ADD == 'pre_add'
        assert ActivityM2mAction.PRE_CLEAR == 'pre_clear'
        assert ActivityM2mAction.PRE_REMOVE == 'pre_remove'

    def test_verbs_are_stored_as_plain_strings(self) -> None:
        user = AuthUser.objects.create_user(username='enumactor', first_name='E', last_name='A')

        set_current_user(user)
        Task.objects.create(name='One')
        set_current_user(None)

        assert Activity.objects.filter(verb=ActivityVerb.CREATED).count() == 1
        assert Activity.objects.filter(verb='created').count() == 1
