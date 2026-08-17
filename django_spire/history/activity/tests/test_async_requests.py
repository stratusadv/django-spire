from __future__ import annotations

from asgiref.sync import sync_to_async

from django.test import AsyncClient, TransactionTestCase
from django.urls import reverse

from django_spire.auth.group.models import AuthGroup
from django_spire.auth.user.models import AuthUser
from django_spire.history.activity.context import get_current_user, set_current_user
from django_spire.history.activity.models import Activity


class AsyncRequestTestCase(TransactionTestCase):
    def setUp(self) -> None:
        self.user = AuthUser.objects.create_superuser(
            username='asyncactor',
            first_name='Async',
            last_name='Actor',
        )

    def tearDown(self) -> None:
        set_current_user(None)

    async def logged_in_client(self, user: AuthUser) -> AsyncClient:
        client = AsyncClient()
        await sync_to_async(client.force_login)(user)

        return client

    async def post_group_form(self, client: AsyncClient, name: str):
        url = reverse('django_spire:auth:group:form:form', kwargs={'pk': 0})
        data = {'name': name}

        return await client.post(url, data=data)


class TestAsyncRequestActivity(AsyncRequestTestCase):
    async def test_create_through_an_async_request_logs_created(self) -> None:
        client = await self.logged_in_client(self.user)

        response = await self.post_group_form(client, 'Async Group')

        assert response.status_code == 302

        group = await AuthGroup.objects.aget(name='Async Group')
        activity = await Activity.objects.aget(verb='created')

        assert activity.object_id == group.pk
        assert activity.user_id == self.user.pk
        assert 'Async Actor created' in activity.information

    async def test_update_through_an_async_request_logs_updated(self) -> None:
        client = await self.logged_in_client(self.user)
        group = await AuthGroup.objects.acreate(name='Async Group')

        url = reverse('django_spire:auth:group:form:form', kwargs={'pk': group.pk})
        data = {'name': 'Async Group Renamed'}

        response = await client.post(url, data=data)

        assert response.status_code == 302

        activity = await Activity.objects.aget(verb='updated')

        assert activity.object_id == group.pk
        assert activity.user_id == self.user.pk

    async def test_delete_through_an_async_request_logs_deleted(self) -> None:
        client = await self.logged_in_client(self.user)
        group = await AuthGroup.objects.acreate(name='Doomed Async Group')
        group_pk = group.pk

        url = reverse('django_spire:auth:group:form:delete', kwargs={'pk': group_pk})
        data = {'should_delete': True}

        response = await client.post(url, data=data)

        deleted_activities = Activity.objects.filter(verb='deleted', object_id=group_pk)

        assert response.status_code == 302
        assert await deleted_activities.acount() == 1
        assert await AuthGroup.objects.filter(pk=group_pk).acount() == 0

    async def test_anonymous_async_request_logs_nothing(self) -> None:
        client = AsyncClient()

        url = reverse('django_spire:auth:group:form:form', kwargs={'pk': 0})
        data = {'name': 'Anonymous Group'}

        await client.post(url, data=data)

        assert await AuthGroup.objects.filter(name='Anonymous Group').acount() == 0
        assert await Activity.objects.acount() == 0

    async def test_sequential_async_requests_attribute_their_own_users(self) -> None:
        other_user = await AuthUser.objects.acreate_superuser(
            username='asyncother',
            first_name='Other',
            last_name='Actor',
        )

        client = await self.logged_in_client(self.user)
        other_client = await self.logged_in_client(other_user)

        await self.post_group_form(client, 'First Async Group')
        await self.post_group_form(other_client, 'Second Async Group')

        first_group = await AuthGroup.objects.aget(name='First Async Group')
        second_group = await AuthGroup.objects.aget(name='Second Async Group')

        first_activity = await Activity.objects.aget(object_id=first_group.pk, verb='created')
        second_activity = await Activity.objects.aget(object_id=second_group.pk, verb='created')

        assert first_activity.user_id == self.user.pk
        assert second_activity.user_id == other_user.pk

    async def test_async_request_does_not_leak_the_user_into_the_caller(self) -> None:
        client = await self.logged_in_client(self.user)

        await self.post_group_form(client, 'Async Group')

        assert get_current_user() is None

    async def test_async_get_request_logs_nothing(self) -> None:
        client = await self.logged_in_client(self.user)

        response = await client.get(reverse('django_spire:auth:group:page:list'))

        assert response.status_code == 200
        assert await Activity.objects.acount() == 0

    async def test_async_bulk_write_inside_a_request_logs_every_row(self) -> None:
        client = await self.logged_in_client(self.user)

        url = reverse('django_spire:auth:group:form:form', kwargs={'pk': 0})

        await client.post(url, data={'name': 'First Async Group'})
        await client.post(url, data={'name': 'Second Async Group'})

        assert await Activity.objects.filter(verb='created').acount() == 2
