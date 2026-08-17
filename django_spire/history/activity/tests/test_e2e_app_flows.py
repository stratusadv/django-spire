from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse

from django_spire.api.models import ApiAccess
from django_spire.auth.user.models import AuthUser
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.help_desk.models import HelpDeskTicket
from django_spire.help_desk.tests.factories import (
    create_test_helpdesk_ticket,
    create_test_helpdesk_ticket_data
)
from django_spire.history.activity.context import (
    activity_user,
    get_current_user,
    set_current_user
)
from django_spire.history.activity.models import Activity
from django_spire.knowledge.collection.models import Collection
from django_spire.knowledge.collection.tests.factories import create_test_collection
from django_spire.knowledge.entry.models import Entry
from django_spire.knowledge.entry.tests.factories import create_test_entry
from django_spire.metric.domain.models import Domain, SubDomain
from django_spire.metric.domain.tests.factories import create_test_domain, create_test_subdomain

from test_project.app.comment.models import CommentExample
from test_project.app.task.models import Task

if TYPE_CHECKING:
    from django_spire.comment.models import Comment


class ActivityFlowTestCase(BaseTestCase):
    def tearDown(self) -> None:
        set_current_user(None)

    def activities_for(self, model: type, object_id: int, verb: str | None = None):
        queryset = Activity.objects.filter(
            content_type=ContentType.objects.get_for_model(model),
            object_id=object_id,
        )

        if verb is None:
            return queryset

        return queryset.filter(verb=verb)


class TestTaskFlowActivity(ActivityFlowTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.task = Task.objects.create(name='One')

    def test_delete_view_logs_deleted_once(self) -> None:
        url = reverse('task:form:delete', kwargs={'pk': self.task.pk})

        response = self.client.post(url)

        self.task.refresh_from_db()

        assert response.status_code == 302
        assert self.task.is_deleted is True
        assert self.activities_for(Task, self.task.pk, 'deleted').count() == 1
        assert self.activities_for(Task, self.task.pk, 'updated').count() == 0

    def test_delete_modal_view_logs_deleted_once(self) -> None:
        url = reverse('task:form:delete_modal', kwargs={'pk': self.task.pk})

        response = self.client.post(url)

        assert response.status_code == 302
        assert self.activities_for(Task, self.task.pk, 'deleted').count() == 1

    def test_delete_view_is_attributed_to_the_request_user(self) -> None:
        url = reverse('task:form:delete', kwargs={'pk': self.task.pk})

        self.client.post(url)

        activity = self.activities_for(Task, self.task.pk, 'deleted').first()

        assert activity.user == self.super_user
        assert 'deleted Task "One"' in activity.information

    def test_delete_view_on_an_already_deleted_task_logs_updated(self) -> None:
        deleted_task = Task.objects.create(name='Gone', is_deleted=True)
        url = reverse('task:form:delete', kwargs={'pk': deleted_task.pk})

        self.client.post(url)

        assert self.activities_for(Task, deleted_task.pk, 'deleted').count() == 0
        assert self.activities_for(Task, deleted_task.pk, 'updated').count() == 1

    def test_get_on_the_delete_view_logs_nothing(self) -> None:
        url = reverse('task:form:delete', kwargs={'pk': self.task.pk})

        response = self.client.get(url)

        assert response.status_code == 200
        assert Activity.objects.count() == 0

    def test_missing_task_delete_request_does_not_leak_the_user(self) -> None:
        url = reverse('task:form:delete', kwargs={'pk': 999999})

        response = self.client.post(url)

        assert response.status_code == 404
        assert get_current_user() is None
        assert Activity.objects.count() == 0


class TestHelpDeskFlowActivity(ActivityFlowTestCase):
    def test_ticket_delete_view_logs_deleted(self) -> None:
        ticket = create_test_helpdesk_ticket()
        url = reverse('django_spire:help_desk:form:delete', kwargs={'pk': ticket.pk})

        response = self.client.post(url)

        ticket.refresh_from_db()

        assert response.status_code == 302
        assert ticket.is_deleted is True
        assert self.activities_for(HelpDeskTicket, ticket.pk, 'deleted').count() == 1

    def test_service_save_logs_created_for_the_ambient_user(self) -> None:
        ticket = HelpDeskTicket()
        ticket_data = create_test_helpdesk_ticket_data()

        with activity_user(self.super_user):
            saved_ticket = ticket.services.save_model_obj(user=self.super_user, **ticket_data)

        activities = self.activities_for(HelpDeskTicket, saved_ticket.pk, 'created')

        assert saved_ticket.created_by == self.super_user
        assert activities.count() == 1
        assert activities.first().user == self.super_user

    def test_service_save_without_an_ambient_user_logs_nothing(self) -> None:
        ticket = HelpDeskTicket()
        ticket_data = create_test_helpdesk_ticket_data()

        saved_ticket = ticket.services.save_model_obj(user=self.super_user, **ticket_data)

        assert saved_ticket.created_by == self.super_user
        assert self.activities_for(HelpDeskTicket, saved_ticket.pk).count() == 0


class TestApiAccessFlowActivity(ActivityFlowTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.access = ApiAccess.objects.create(name='Test Access')
        self.url = reverse('django_spire:api:page:delete', kwargs={'pk': self.access.pk})

    def test_delete_view_logs_deleted(self) -> None:
        response = self.client.post(self.url, data={'should_delete': True})

        self.access.refresh_from_db()

        assert response.status_code == 302
        assert self.access.is_deleted is True
        assert self.activities_for(ApiAccess, self.access.pk, 'deleted').count() == 1

    def test_delete_view_without_confirmation_logs_nothing(self) -> None:
        response = self.client.post(self.url, data={})

        self.access.refresh_from_db()

        assert response.status_code == 302
        assert self.access.is_deleted is False
        assert Activity.objects.count() == 0


class TestKnowledgeFlowActivity(ActivityFlowTestCase):
    def test_collection_delete_view_logs_deleted(self) -> None:
        collection = create_test_collection()
        url = reverse(
            'django_spire:knowledge:collection:page:delete',
            kwargs={'pk': collection.pk},
        )

        response = self.client.post(url, data={'should_delete': True})

        collection.refresh_from_db()

        assert response.status_code == 302
        assert collection.is_deleted is True
        assert self.activities_for(Collection, collection.pk, 'deleted').count() == 1

    def test_entry_delete_view_logs_deleted(self) -> None:
        entry = create_test_entry()
        url = reverse('django_spire:knowledge:entry:page:delete', kwargs={'pk': entry.pk})

        response = self.client.post(url, data={'should_delete': True})

        entry.refresh_from_db()

        assert response.status_code == 302
        assert entry.is_deleted is True
        assert self.activities_for(Entry, entry.pk, 'deleted').count() == 1


class TestMetricDomainFlowActivity(ActivityFlowTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.domain = create_test_domain()

    def test_domain_delete_view_logs_deleted(self) -> None:
        url = reverse('django_spire:metric:domain:form:delete', kwargs={'pk': self.domain.pk})

        response = self.client.post(url, data={'should_delete': True})

        self.domain.refresh_from_db()

        assert response.status_code == 302
        assert self.domain.is_deleted is True
        assert self.activities_for(Domain, self.domain.pk, 'deleted').count() == 1

    def test_subdomain_delete_view_logs_deleted(self) -> None:
        subdomain = create_test_subdomain(domain=self.domain)

        url = reverse(
            'django_spire:metric:domain:form:delete_subdomain',
            kwargs={'domain_pk': self.domain.pk, 'pk': subdomain.pk},
        )

        response = self.client.post(url, data={'should_delete': True})

        subdomain.refresh_from_db()

        assert response.status_code == 302
        assert subdomain.is_deleted is True
        assert self.activities_for(SubDomain, subdomain.pk, 'deleted').count() == 1


class TestCommentFlowActivity(ActivityFlowTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.example = CommentExample.objects.create(name='Example')
        self.comment = self.example.add_comment(user=self.super_user, information='hello')

        self.url_kwargs = {
            'obj_pk': self.example.pk,
            'app_label': 'test_project_comment',
            'model_name': 'commentexample',
        }

    def create_url(self) -> str:
        kwargs = {'comment_pk': 0, **self.url_kwargs}

        return reverse('django_spire:comment:form', kwargs=kwargs)

    def delete_url(self, comment: Comment) -> str:
        kwargs = {'comment_pk': comment.pk, **self.url_kwargs}

        return reverse('django_spire:comment:delete_form', kwargs=kwargs)

    def test_create_view_adds_a_comment(self) -> None:
        response = self.client.post(self.create_url(), data={'information': 'second'})

        assert response.status_code == 302
        assert self.example.comments.count() == 2

    def test_create_view_records_no_activity_on_the_parent(self) -> None:
        self.client.post(self.create_url(), data={'information': 'second'})

        assert self.activities_for(CommentExample, self.example.pk).count() == 0

    def test_delete_view_soft_deletes_the_comment(self) -> None:
        response = self.client.post(self.delete_url(self.comment), data={'should_delete': True})

        self.comment.refresh_from_db()

        assert response.status_code == 302
        assert self.comment.is_deleted is True

    def test_delete_view_records_no_activity_on_the_parent(self) -> None:
        self.client.post(self.delete_url(self.comment), data={'should_delete': True})

        assert self.activities_for(CommentExample, self.example.pk).count() == 0
        assert Activity.objects.count() == 0


class TestSessionFlowActivity(ActivityFlowTestCase):
    def test_login_request_logs_nothing(self) -> None:
        password = 'loginpassword123'  # noqa: S105
        user = AuthUser.objects.create_user(username='loginuser')
        user.set_password(password)
        user.save()

        Activity.objects.all().delete()

        client = Client()
        login_data = {'username': 'loginuser', 'password': password}

        response = client.post(reverse('django_spire:auth:admin:login'), data=login_data)

        assert response.status_code == 302
        assert Activity.objects.count() == 0

    def test_anonymous_delete_request_changes_nothing(self) -> None:
        task = Task.objects.create(name='One')

        client = Client()
        response = client.post(reverse('task:form:delete', kwargs={'pk': task.pk}))

        task.refresh_from_db()

        assert response.status_code == 302
        assert task.is_deleted is False
        assert Activity.objects.count() == 0

    def test_requests_are_attributed_to_the_authenticated_user_of_each_request(self) -> None:
        other_user = AuthUser.objects.create_superuser(
            username='flowother',
            first_name='Other',
            last_name='Actor',
        )

        first_task = Task.objects.create(name='First')
        second_task = Task.objects.create(name='Second')

        self.client.post(reverse('task:form:delete', kwargs={'pk': first_task.pk}))

        self.client.force_login(other_user)
        self.client.post(reverse('task:form:delete', kwargs={'pk': second_task.pk}))

        first_activity = self.activities_for(Task, first_task.pk, 'deleted').first()
        second_activity = self.activities_for(Task, second_task.pk, 'deleted').first()

        assert first_activity.user == self.super_user
        assert second_activity.user == other_user

    def test_context_is_cleared_between_requests(self) -> None:
        task = Task.objects.create(name='One')

        self.client.post(reverse('task:form:delete', kwargs={'pk': task.pk}))

        assert get_current_user() is None
