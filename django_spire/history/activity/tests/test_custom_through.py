from __future__ import annotations

from django.db import connection, models
from django.db.models.signals import m2m_changed
from django.test import TransactionTestCase

from django_spire.auth.user.models import AuthUser
from django_spire.history.activity.context import activity_user, set_current_user
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.activity.models import Activity
from django_spire.history.activity.signals import connect_activity_signals
from django_spire.history.mixins import HistoryModelMixin
from django_spire.history.querysets import HistoryQuerySet


class ThroughMember(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=32)

    objects = HistoryQuerySet.as_manager()

    class Meta:
        app_label = 'test_project_task'

    def __str__(self) -> str:
        return self.name


class ThroughTeam(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=32)

    members = models.ManyToManyField(
        ThroughMember,
        through='ThroughMembership',
        related_name='teams',
    )

    objects = HistoryQuerySet.as_manager()

    class Meta:
        app_label = 'test_project_task'

    def __str__(self) -> str:
        return self.name


class ThroughMembership(models.Model):
    member = models.ForeignKey(ThroughMember, on_delete=models.CASCADE)
    team = models.ForeignKey(ThroughTeam, on_delete=models.CASCADE)
    role = models.CharField(max_length=32, default='')

    class Meta:
        app_label = 'test_project_task'

    def __str__(self) -> str:
        return f'{self.member} - {self.team}'


class ThroughNode(ActivityMixin, HistoryModelMixin):
    name = models.CharField(max_length=32)

    links = models.ManyToManyField(
        'self',
        through='ThroughLink',
        through_fields=('from_node', 'to_node'),
        symmetrical=False,
        related_name='linked_by',
    )

    objects = HistoryQuerySet.as_manager()

    class Meta:
        app_label = 'test_project_task'

    def __str__(self) -> str:
        return self.name


class ThroughLink(models.Model):
    from_node = models.ForeignKey(
        ThroughNode,
        on_delete=models.CASCADE,
        related_name='outgoing_links',
    )

    to_node = models.ForeignKey(
        ThroughNode,
        on_delete=models.CASCADE,
        related_name='incoming_links',
    )

    label = models.CharField(max_length=32, default='')

    class Meta:
        app_label = 'test_project_task'

    def __str__(self) -> str:
        return f'{self.from_node} - {self.to_node}'


THROUGH_MODELS = [
    ThroughMember,
    ThroughTeam,
    ThroughMembership,
    ThroughNode,
    ThroughLink,
]


class CustomThroughTestCase(TransactionTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        with connection.schema_editor() as editor:
            for model in THROUGH_MODELS:
                editor.create_model(model)

        connect_activity_signals()

    @classmethod
    def tearDownClass(cls) -> None:
        with connection.schema_editor() as editor:
            for model in reversed(THROUGH_MODELS):
                editor.delete_model(model)

        super().tearDownClass()

    def setUp(self) -> None:
        self.user = AuthUser.objects.create_user(
            username='throughactor',
            first_name='Through',
            last_name='Actor',
        )

    def tearDown(self) -> None:
        set_current_user(None)


class TestCustomThroughRegistration(CustomThroughTestCase):
    def test_custom_through_model_has_a_listener(self) -> None:
        assert m2m_changed.has_listeners(ThroughMembership) is True

    def test_self_referential_custom_through_model_has_a_listener(self) -> None:
        assert m2m_changed.has_listeners(ThroughLink) is True


class TestCustomThroughForwardActivity(CustomThroughTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.team = ThroughTeam.objects.create(name='Team One')
        self.member = ThroughMember.objects.create(name='Member A')

        Activity.objects.all().delete()

    def test_add_logs_added_on_the_team(self) -> None:
        with activity_user(self.user):
            self.team.members.add(self.member)

        activities = Activity.objects.filter(verb='added')

        assert activities.count() == 1
        assert activities.first().object_id == self.team.pk
        assert 'added 1 through member to' in activities.first().information
        assert '(Member A)' in activities.first().information

    def test_add_with_through_defaults_stores_the_extra_field(self) -> None:
        through_defaults = {'role': 'lead'}

        with activity_user(self.user):
            self.team.members.add(self.member, through_defaults=through_defaults)

        membership = ThroughMembership.objects.get(team=self.team, member=self.member)

        assert membership.role == 'lead'
        assert Activity.objects.filter(verb='added').count() == 1

    def test_adding_an_existing_member_logs_nothing(self) -> None:
        self.team.members.add(self.member)
        Activity.objects.all().delete()

        with activity_user(self.user):
            self.team.members.add(self.member)

        assert Activity.objects.filter(verb='added').count() == 0

    def test_remove_logs_removed_on_the_team(self) -> None:
        self.team.members.add(self.member)
        Activity.objects.all().delete()

        with activity_user(self.user):
            self.team.members.remove(self.member)

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert activities.first().object_id == self.team.pk
        assert 'removed 1 through member from' in activities.first().information

    def test_removing_a_non_member_logs_nothing(self) -> None:
        with activity_user(self.user):
            self.team.members.remove(self.member)

        assert Activity.objects.filter(verb='removed').count() == 0

    def test_clear_logs_the_removed_count_and_names(self) -> None:
        other_member = ThroughMember.objects.create(name='Member B')
        self.team.members.add(self.member, other_member)
        Activity.objects.all().delete()

        with activity_user(self.user):
            self.team.members.clear()

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert 'removed 2 through members from' in activities.first().information
        assert '(Member A, Member B)' in activities.first().information

    def test_clear_when_empty_logs_nothing(self) -> None:
        with activity_user(self.user):
            self.team.members.clear()

        assert Activity.objects.filter(verb='removed').count() == 0

    def test_set_logs_added_and_removed(self) -> None:
        other_member = ThroughMember.objects.create(name='Member B')
        self.team.members.add(self.member)
        Activity.objects.all().delete()

        with activity_user(self.user):
            self.team.members.set([other_member])

        assert Activity.objects.filter(verb='added').count() == 1
        assert Activity.objects.filter(verb='removed').count() == 1

    def test_without_a_user_logs_nothing(self) -> None:
        self.team.members.add(self.member)

        assert Activity.objects.count() == 0


class TestCustomThroughReverseActivity(CustomThroughTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.team = ThroughTeam.objects.create(name='Team One')
        self.member = ThroughMember.objects.create(name='Member A')

        Activity.objects.all().delete()

    def test_reverse_add_logs_on_the_member(self) -> None:
        with activity_user(self.user):
            self.member.teams.add(self.team)

        activities = Activity.objects.filter(verb='added')

        assert activities.count() == 1
        assert activities.first().object_id == self.member.pk
        assert 'added 1 through team to' in activities.first().information
        assert '(Team One)' in activities.first().information

    def test_reverse_remove_logs_on_the_member(self) -> None:
        self.member.teams.add(self.team)
        Activity.objects.all().delete()

        with activity_user(self.user):
            self.member.teams.remove(self.team)

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert activities.first().object_id == self.member.pk
        assert 'removed 1 through team from' in activities.first().information

    def test_reverse_remove_of_a_non_member_logs_nothing(self) -> None:
        with activity_user(self.user):
            self.member.teams.remove(self.team)

        assert Activity.objects.filter(verb='removed').count() == 0

    def test_reverse_clear_logs_the_incoming_count(self) -> None:
        other_team = ThroughTeam.objects.create(name='Team Two')
        self.member.teams.add(self.team, other_team)
        Activity.objects.all().delete()

        with activity_user(self.user):
            self.member.teams.clear()

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert activities.first().object_id == self.member.pk
        assert 'removed 2 through teams from' in activities.first().information


class TestSelfReferentialCustomThroughActivity(CustomThroughTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.node_a = ThroughNode.objects.create(name='Node A')
        self.node_b = ThroughNode.objects.create(name='Node B')

        Activity.objects.all().delete()

    def test_forward_add_logs_on_the_source_node(self) -> None:
        with activity_user(self.user):
            self.node_a.links.add(self.node_b)

        activities = Activity.objects.filter(verb='added')

        assert activities.count() == 1
        assert activities.first().object_id == self.node_a.pk
        assert '(Node B)' in activities.first().information

    def test_forward_remove_logs_on_the_source_node(self) -> None:
        self.node_a.links.add(self.node_b)
        Activity.objects.all().delete()

        with activity_user(self.user):
            self.node_a.links.remove(self.node_b)

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert activities.first().object_id == self.node_a.pk

    def test_reverse_add_logs_on_the_target_node(self) -> None:
        with activity_user(self.user):
            self.node_b.linked_by.add(self.node_a)

        activities = Activity.objects.filter(verb='added')

        assert activities.count() == 1
        assert activities.first().object_id == self.node_b.pk
        assert '(Node A)' in activities.first().information

    def test_forward_clear_counts_only_outgoing_links(self) -> None:
        self.node_a.links.add(self.node_b)
        self.node_b.links.add(self.node_a)
        Activity.objects.all().delete()

        with activity_user(self.user):
            self.node_a.links.clear()

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert 'removed 1 through node from' in activities.first().information
        assert self.node_b.links.filter(pk=self.node_a.pk).exists()

    def test_reverse_clear_counts_only_incoming_links(self) -> None:
        node_c = ThroughNode.objects.create(name='Node C')
        self.node_a.links.add(self.node_b)
        node_c.links.add(self.node_b)
        Activity.objects.all().delete()

        with activity_user(self.user):
            self.node_b.linked_by.clear()

        activities = Activity.objects.filter(verb='removed')

        assert activities.count() == 1
        assert activities.first().object_id == self.node_b.pk
        assert 'removed 2 through nodes from' in activities.first().information


class TestDirectThroughRowWrites(CustomThroughTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.team = ThroughTeam.objects.create(name='Team One')
        self.member = ThroughMember.objects.create(name='Member A')

        Activity.objects.all().delete()

    def test_creating_a_through_row_directly_logs_nothing(self) -> None:
        with activity_user(self.user):
            ThroughMembership.objects.create(team=self.team, member=self.member)

        assert self.team.members.count() == 1
        assert Activity.objects.count() == 0

    def test_deleting_a_through_row_directly_logs_nothing(self) -> None:
        membership = ThroughMembership.objects.create(team=self.team, member=self.member)

        with activity_user(self.user):
            membership.delete()

        assert self.team.members.count() == 0
        assert Activity.objects.count() == 0
