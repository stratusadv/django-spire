from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser
from django_spire.core.tests.test_cases import BaseTestCase
from django_spire.history.activity.context import get_current_user, set_current_user
from django_spire.history.activity.middleware import ActivityUserMiddleware
from django_spire.history.activity.models import Activity

from test_project.app.model_and_service.models import Adult
from test_project.app.task.models import Task

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest


class ActivityEndToEndTestCase(BaseTestCase):
    def tearDown(self) -> None:
        set_current_user(None)

    def activities_for(self, model: type, object_id: int, verb: str):
        return Activity.objects.filter(
            content_type=ContentType.objects.get_for_model(model),
            object_id=object_id,
            verb=verb,
        )


class TestCreateEndToEnd(ActivityEndToEndTestCase):
    def test_form_create_logs_created(self) -> None:
        url = reverse('django_spire:auth:group:form:form', kwargs={'pk': 0})

        response = self.client.post(url, data={'name': 'Editors'})

        assert response.status_code == 302
        group = AuthGroup.objects.get(name='Editors')

        activities = self.activities_for(AuthGroup, group.pk, 'created')

        assert activities.count() == 1
        assert activities.first().user == self.super_user

    def test_form_create_logs_exactly_one_activity(self) -> None:
        url = reverse('django_spire:auth:group:form:form', kwargs={'pk': 0})

        self.client.post(url, data={'name': 'Editors'})

        assert Activity.objects.count() == 1


class TestUpdateEndToEnd(ActivityEndToEndTestCase):
    def test_form_update_logs_updated(self) -> None:
        group = AuthGroup.objects.create(name='Editors')
        url = reverse('django_spire:auth:group:form:form', kwargs={'pk': group.pk})

        response = self.client.post(url, data={'name': 'Editors Renamed'})

        assert response.status_code == 302

        activities = self.activities_for(AuthGroup, group.pk, 'updated')

        assert activities.count() == 1
        assert activities.first().user == self.super_user
        assert 'Editors Renamed' in activities.first().information


class TestDeleteEndToEnd(ActivityEndToEndTestCase):
    def test_form_delete_logs_deleted(self) -> None:
        group = AuthGroup.objects.create(name='Doomed')
        group_pk = group.pk
        url = reverse('django_spire:auth:group:form:delete', kwargs={'pk': group.pk})

        response = self.client.post(url, data={'should_delete': True})

        assert response.status_code == 302
        assert AuthGroup.objects.filter(pk=group_pk).count() == 0

        activities = self.activities_for(AuthGroup, group_pk, 'deleted')

        assert activities.count() == 1
        assert activities.first().user == self.super_user

    def test_soft_delete_logs_deleted(self) -> None:
        task = Task.objects.create(name='Soft Deleted Task')
        url = reverse('task:form:delete', kwargs={'pk': task.pk})

        response = self.client.post(url)

        assert response.status_code == 302

        task.refresh_from_db()
        assert task.is_deleted is True

        assert self.activities_for(Task, task.pk, 'deleted').count() == 1
        assert self.activities_for(Task, task.pk, 'updated').count() == 0


class TestM2MEndToEnd(ActivityEndToEndTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = AuthUser.objects.create_user(
            username='member',
            password='testpass',  # noqa: S106
            first_name='Member',
            last_name='User',
        )
        self.group = AuthGroup.objects.create(name='Editors')

    def test_group_user_form_logs_added(self) -> None:
        url = reverse('django_spire:auth:group:form:user', kwargs={'pk': self.group.pk})

        response = self.client.post(url, data={'users': [self.member.pk]})

        assert response.status_code == 302
        assert self.member.groups.filter(pk=self.group.pk).count() == 1

        activities = self.activities_for(AuthGroup, self.group.pk, 'added')

        assert activities.count() == 1
        assert activities.first().user == self.super_user
        assert 'added 1' in activities.first().information

    def test_group_remove_user_form_logs_removed(self) -> None:
        self.member.groups.add(self.group)
        url = reverse(
            'django_spire:auth:group:form:user_remove',
            kwargs={'group_pk': self.group.pk, 'pk': self.member.pk},
        )

        response = self.client.post(url)

        assert response.status_code == 302
        assert self.member.groups.count() == 0

        activities = self.activities_for(AuthGroup, self.group.pk, 'removed')

        assert activities.count() == 1
        assert activities.first().user == self.super_user
        assert 'removed 1' in activities.first().information


class TestAnonymousEndToEnd(TestCase):
    def test_anonymous_request_logs_nothing(self) -> None:
        client = Client()

        response = client.get(reverse('test_model:detail'))

        assert response.status_code == 200
        assert Adult.objects.count() == 1
        assert Activity.objects.count() == 0


class TestBulkEndToEnd(ActivityEndToEndTestCase):
    def _run_request_through_middleware(self, handler: Callable[[], None]) -> None:
        def view(_request: HttpRequest) -> HttpResponse:
            handler()
            return HttpResponse()

        request = RequestFactory().post('/')
        request.user = self.super_user

        ActivityUserMiddleware(view)(request)

    def test_bulk_create_in_request_logs_created(self) -> None:
        def handler() -> None:
            Task.objects.bulk_create([Task(name='One'), Task(name='Two')])

        self._run_request_through_middleware(handler)

        activities = Activity.objects.filter(verb='created')

        assert activities.count() == 2
        assert all(activity.user == self.super_user for activity in activities)

    def test_bulk_update_in_request_logs_updated_once(self) -> None:
        tasks = [Task.objects.create(name='One'), Task.objects.create(name='Two')]

        def handler() -> None:
            for task in tasks:
                task.name = f'{task.name} Renamed'

            Task.objects.bulk_update(tasks, ['name'])

        self._run_request_through_middleware(handler)

        assert Activity.objects.filter(verb='updated').count() == 2

    def test_queryset_update_in_request_logs_updated(self) -> None:
        tasks = [Task.objects.create(name='One'), Task.objects.create(name='Two')]

        def handler() -> None:
            Task.objects.filter(pk__in=[task.pk for task in tasks]).update(description='Changed')

        self._run_request_through_middleware(handler)

        assert Activity.objects.filter(verb='updated').count() == 2

    def test_queryset_delete_in_request_logs_deleted(self) -> None:
        tasks = [Task.objects.create(name='One'), Task.objects.create(name='Two')]

        def handler() -> None:
            Task.objects.filter(pk__in=[task.pk for task in tasks]).delete()

        self._run_request_through_middleware(handler)

        assert Activity.objects.filter(verb='deleted').count() == 2


class TestMiddlewareLifecycleEndToEnd(ActivityEndToEndTestCase):
    def test_context_cleared_after_request(self) -> None:
        self.client.get(reverse('django_spire:auth:group:page:list'))

        assert get_current_user() is None

    def test_activity_user_matches_request_user(self) -> None:
        other_user = AuthUser.objects.create_superuser(username='other')

        other_client = Client()
        other_client.force_login(other_user)

        url = reverse('django_spire:auth:group:form:form', kwargs={'pk': 0})
        other_client.post(url, data={'name': 'Other Group'})

        group = AuthGroup.objects.get(name='Other Group')
        activity = self.activities_for(AuthGroup, group.pk, 'created').first()

        assert activity.user == other_user
