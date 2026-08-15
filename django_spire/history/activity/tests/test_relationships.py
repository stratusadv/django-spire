from __future__ import annotations

from django.contrib.auth.models import User
from django.db import connection, models
from django.test import TransactionTestCase

from django_spire.history.activity.context import activity_user, set_current_user
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.activity.models import Activity
from django_spire.history.activity.signals import connect_activity_signals
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.querysets import HistoryQuerySet


class RelationParent(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=32)

    objects = HistoryQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        app_label = 'test_project_task'


class RelationNullChild(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey(
        RelationParent,
        on_delete=models.SET_NULL,
        null=True,
        related_name='null_children',
    )

    objects = HistoryQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        app_label = 'test_project_task'


class RelationOtoChild(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=32)
    parent = models.OneToOneField(
        RelationParent,
        on_delete=models.CASCADE,
        related_name='oto_child',
    )

    objects = HistoryQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        app_label = 'test_project_task'


class RelationMtiChild(RelationParent):
    extra = models.CharField(max_length=32, default='')

    class Meta:
        app_label = 'test_project_task'


class RelationSelfLink(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=32)
    links = models.ManyToManyField('self', symmetrical=False, related_name='linked_by')

    objects = HistoryQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        app_label = 'test_project_task'


class RelationBuddy(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=32)
    buddies = models.ManyToManyField('self')

    objects = HistoryQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        app_label = 'test_project_task'


DYNAMIC_MODELS = [
    RelationParent,
    RelationNullChild,
    RelationOtoChild,
    RelationMtiChild,
    RelationSelfLink,
    RelationBuddy,
]


class TestRelationshipActivity(TransactionTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        with connection.schema_editor() as editor:
            for model in DYNAMIC_MODELS:
                editor.create_model(model)

        connect_activity_signals()

    @classmethod
    def tearDownClass(cls) -> None:
        with connection.schema_editor() as editor:
            for model in reversed(DYNAMIC_MODELS):
                editor.delete_model(model)

        super().tearDownClass()

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username='relationuser',
            password='testpass',  # noqa: S106
            first_name='Relation',
            last_name='User',
        )

    def tearDown(self) -> None:
        set_current_user(None)

    def test_set_null_cascade_logs_only_the_parent_delete(self) -> None:
        parent = RelationParent.objects.create(name='P')
        RelationNullChild.objects.create(name='C1', parent=parent)
        RelationNullChild.objects.create(name='C2', parent=parent)
        Activity.objects.all().delete()

        with activity_user(self.user):
            parent.delete()

        assert Activity.objects.filter(verb='deleted').count() == 1
        assert Activity.objects.filter(verb='updated').count() == 0
        assert RelationNullChild.objects.filter(parent__isnull=True).count() == 2

    def test_one_to_one_cascade_logs_parent_and_child(self) -> None:
        parent = RelationParent.objects.create(name='P')
        child = RelationOtoChild.objects.create(name='O', parent=parent)
        parent_pk = parent.pk
        child_pk = child.pk
        Activity.objects.all().delete()

        with activity_user(self.user):
            parent.delete()

        deleted_activities = Activity.objects.filter(verb='deleted')
        deleted_rows = {
            (activity.content_type.model, activity.object_id)
            for activity in deleted_activities
        }
        expected_rows = {
            ('relationparent', parent_pk),
            ('relationotochild', child_pk),
        }

        assert deleted_activities.count() == 2
        assert deleted_rows == expected_rows

    def test_mti_create_and_update_log_once(self) -> None:
        with activity_user(self.user):
            child = RelationMtiChild.objects.create(name='M', extra='x')

        assert Activity.objects.filter(verb='created').count() == 1

        with activity_user(self.user):
            child.extra = 'y'
            child.save()

        assert Activity.objects.filter(verb='updated').count() == 1

    def test_mti_delete_logs_once_per_table_row(self) -> None:
        child = RelationMtiChild.objects.create(name='M', extra='x')
        Activity.objects.all().delete()

        with activity_user(self.user):
            child.delete()

        assert Activity.objects.filter(verb='deleted').count() == 2

    def test_self_m2m_forward_add_and_remove_log(self) -> None:
        link_a = RelationSelfLink.objects.create(name='a')
        link_b = RelationSelfLink.objects.create(name='b')
        Activity.objects.all().delete()

        with activity_user(self.user):
            link_a.links.add(link_b)
            link_a.links.remove(link_b)
            link_a.links.remove(link_b)

        assert Activity.objects.filter(verb='added').count() == 1
        assert Activity.objects.filter(verb='removed').count() == 1

    def test_self_m2m_reverse_add_logs(self) -> None:
        link_a = RelationSelfLink.objects.create(name='a')
        link_b = RelationSelfLink.objects.create(name='b')
        Activity.objects.all().delete()

        with activity_user(self.user):
            link_b.linked_by.add(link_a)

        added_activities = Activity.objects.filter(verb='added')

        assert added_activities.count() == 1
        assert added_activities.first().object_id == link_b.pk
        assert link_a.links.filter(pk=link_b.pk).exists()

    def test_self_m2m_reverse_remove_logs(self) -> None:
        link_a = RelationSelfLink.objects.create(name='a')
        link_b = RelationSelfLink.objects.create(name='b')
        link_a.links.add(link_b)
        Activity.objects.all().delete()

        with activity_user(self.user):
            link_b.linked_by.remove(link_a)

        removed_activities = Activity.objects.filter(verb='removed')

        assert removed_activities.count() == 1
        assert removed_activities.first().object_id == link_b.pk
        assert not link_a.links.filter(pk=link_b.pk).exists()

    def test_self_m2m_reverse_remove_non_member_logs_nothing(self) -> None:
        link_a = RelationSelfLink.objects.create(name='a')
        link_b = RelationSelfLink.objects.create(name='b')
        Activity.objects.all().delete()

        with activity_user(self.user):
            link_b.linked_by.remove(link_a)

        assert Activity.objects.filter(verb='removed').count() == 0

    def test_self_m2m_reverse_clear_logs_incoming_count(self) -> None:
        link_a = RelationSelfLink.objects.create(name='a')
        link_b = RelationSelfLink.objects.create(name='b')
        link_c = RelationSelfLink.objects.create(name='c')
        link_a.links.add(link_c)
        link_b.links.add(link_c)
        Activity.objects.all().delete()

        with activity_user(self.user):
            link_c.linked_by.clear()

        removed_activities = Activity.objects.filter(verb='removed')

        assert removed_activities.count() == 1
        assert removed_activities.first().object_id == link_c.pk
        assert 'removed 2' in removed_activities.first().information

    def test_self_m2m_forward_clear_logs_outgoing_count(self) -> None:
        link_a = RelationSelfLink.objects.create(name='a')
        link_b = RelationSelfLink.objects.create(name='b')
        link_a.links.add(link_b)
        link_b.links.add(link_a)
        Activity.objects.all().delete()

        with activity_user(self.user):
            link_a.links.clear()

        removed_activities = Activity.objects.filter(verb='removed')

        assert removed_activities.count() == 1
        assert removed_activities.first().object_id == link_a.pk
        assert 'removed 1' in removed_activities.first().information
        assert link_b.links.filter(pk=link_a.pk).exists()

    def test_symmetrical_m2m_logs_once_per_operation(self) -> None:
        buddy_a = RelationBuddy.objects.create(name='a')
        buddy_b = RelationBuddy.objects.create(name='b')
        Activity.objects.all().delete()

        with activity_user(self.user):
            buddy_a.buddies.add(buddy_b)

        assert Activity.objects.filter(verb='added').count() == 1

        with activity_user(self.user):
            buddy_a.buddies.remove(buddy_b)

        assert Activity.objects.filter(verb='removed').count() == 1
