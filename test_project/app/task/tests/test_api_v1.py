from __future__ import annotations

import json

from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from django_spire.api.choices import ApiPermissionChoices
from django_spire.api.models import ApiAccess
from django_spire.constants import BASE_URL_NAME
from django_spire.core.tests.test_cases import BaseTestCase

from test_project.app.task.choices import TaskStatusChoices, TaskUserRoleChoices
from test_project.app.task.models import Task, TaskUser


class TaskApiTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.raw_api_key = 'task_test_api_key'
        self.api_access = ApiAccess.objects.create(
            name='Task API',
            permission=ApiPermissionChoices.DELETE,
            user=self.super_user,
            has_super_access=True,
        )
        self.api_access.set_key_and_save(self.raw_api_key)

        self.worker_user = User.objects.create_user(
            username='worker', first_name='Jo', last_name='Smith'
        )

        self.parent_task = self.create_task(name='Parent Task')
        self.child_task = self.create_task(name='Child Task', parent=self.parent_task)
        self.done_task = self.create_task(name='Done Task', status=TaskStatusChoices.DONE)

    def api_extra(self) -> dict:
        return {'HTTP_X_API_KEY': self.raw_api_key}

    def create_task(self, **kwargs) -> Task:
        defaults = {'name': 'Test Task', 'status': TaskStatusChoices.NEW}
        defaults.update(kwargs)
        task = Task.objects.create(**defaults)
        task.refresh_from_db()
        return task

    def list_url(self) -> str:
        return reverse(f'{BASE_URL_NAME}:api_v1:list_tasks')

    def detail_url(self, task_id: int) -> str:
        return reverse(f'{BASE_URL_NAME}:api_v1:task_detail', kwargs={'task_id': task_id})

    def users_url(self, task_id: int) -> str:
        return reverse(f'{BASE_URL_NAME}:api_v1:list_task_users', kwargs={'task_id': task_id})

    def complete_url(self, task_id: int) -> str:
        return reverse(f'{BASE_URL_NAME}:api_v1:complete_task', kwargs={'task_id': task_id})

    def post_json(self, url: str, payload: dict, extra: dict | None = None):
        return self.client.post(
            url, data=json.dumps(payload), content_type='application/json', **(extra or {})
        )

    def create_user_key(
        self, username: str, permission_codenames: str | list[str], api_permission: int
    ) -> tuple[str, User]:
        if isinstance(permission_codenames, str):
            permission_codenames = [permission_codenames]

        user = User.objects.create_user(username=username)
        content_type = ContentType.objects.get_for_model(Task)
        for codename in permission_codenames:
            user.user_permissions.add(
                Permission.objects.get(content_type=content_type, codename=codename)
            )

        raw_key = f'{username}_key'
        api_access = ApiAccess.objects.create(name=username, permission=api_permission, user=user)
        api_access.set_key_and_save(raw_key)

        return raw_key, user


class TaskApiAuthorizationTestCase(TaskApiTestCase):
    def test_key_without_linked_user_is_rejected(self) -> None:
        orphan_access = ApiAccess.objects.create(
            name='Orphan', permission=ApiPermissionChoices.DELETE
        )
        orphan_access.set_key_and_save('orphan_key')

        response = self.client.get(self.list_url(), HTTP_X_API_KEY='orphan_key')

        assert response.status_code == 401

    def test_user_without_view_permission_is_rejected(self) -> None:
        raw_key, _user = self.create_user_key('no_view', 'add_task', ApiPermissionChoices.VIEW)

        response = self.client.get(self.list_url(), HTTP_X_API_KEY=raw_key)

        assert response.status_code == 401

    def test_user_with_view_permission_can_read(self) -> None:
        raw_key, _user = self.create_user_key('reader', 'view_task', ApiPermissionChoices.VIEW)

        response = self.client.get(self.list_url(), HTTP_X_API_KEY=raw_key)

        assert response.status_code == 200
        assert response.json()['count'] == 3

    def test_user_with_view_permission_cannot_create(self) -> None:
        raw_key, _user = self.create_user_key('reader', 'view_task', ApiPermissionChoices.VIEW)

        response = self.post_json(
            self.list_url(), {'name': 'New Task'}, {'HTTP_X_API_KEY': raw_key}
        )

        assert response.status_code == 401
        assert not Task.objects.filter(name='New Task').exists()

    def test_super_access_key_bypasses_user_permission(self) -> None:
        super_access = ApiAccess.objects.create(
            name='Super Key', permission=ApiPermissionChoices.VIEW
        )
        super_access.has_super_access = True
        super_access.set_key_and_save('super_key')

        read_response = self.client.get(self.list_url(), HTTP_X_API_KEY='super_key')
        assert read_response.status_code == 200
        assert read_response.json()['count'] == 3

    def test_super_access_key_bypasses_api_permission_on_writes(self) -> None:
        super_access = ApiAccess.objects.create(
            name='Super Key', permission=ApiPermissionChoices.VIEW
        )
        super_access.has_super_access = True
        super_access.set_key_and_save('super_key')

        delete_response = self.client.delete(
            self.detail_url(self.parent_task.id), HTTP_X_API_KEY='super_key'
        )

        assert delete_response.status_code == 200
        self.parent_task.refresh_from_db()
        assert self.parent_task.is_deleted is True

    def test_super_access_still_rejects_missing_key(self) -> None:
        super_access = ApiAccess.objects.create(
            name='Super Key', permission=ApiPermissionChoices.VIEW
        )
        super_access.has_super_access = True
        super_access.set_key_and_save('super_key')

        response = self.client.get(self.list_url())

        assert response.status_code == 401


class ListTasksApiTestCase(TaskApiTestCase):
    def test_list_tasks_requires_api_key(self) -> None:
        response = self.client.get(self.list_url())

        assert response.status_code == 401

    def test_list_tasks_returns_visible_tasks(self) -> None:
        response = self.client.get(self.list_url(), **self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert body['count'] == 3
        names = [result['name'] for result in body['results']]
        assert names == ['Parent Task', 'Child Task', 'Done Task']

    def test_list_tasks_excludes_deleted(self) -> None:
        self.parent_task.set_deleted()

        response = self.client.get(self.list_url(), **self.api_extra())

        assert response.status_code == 200
        assert response.json()['count'] == 2

    def test_list_tasks_search_filter(self) -> None:
        response = self.client.get(self.list_url(), {'search': 'Child'}, **self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert body['count'] == 1
        assert body['results'][0]['name'] == 'Child Task'

    def test_list_tasks_status_filter(self) -> None:
        response = self.client.get(
            self.list_url(), {'status': TaskStatusChoices.DONE}, **self.api_extra()
        )

        assert response.status_code == 200
        body = response.json()
        assert body['count'] == 1
        assert body['results'][0]['name'] == 'Done Task'

    def test_list_tasks_parent_id_filter(self) -> None:
        response = self.client.get(
            self.list_url(), {'parent_id': self.parent_task.id}, **self.api_extra()
        )

        assert response.status_code == 200
        body = response.json()
        assert body['count'] == 1
        assert body['results'][0]['id'] == self.child_task.id

    def test_list_tasks_pagination(self) -> None:
        response = self.client.get(self.list_url(), {'limit': 2, 'offset': 1}, **self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert body['count'] == 3
        assert len(body['results']) == 2
        assert body['results'][0]['id'] == self.child_task.id


class CreateTaskApiTestCase(TaskApiTestCase):
    def test_create_task_requires_add_api_permission_level(self) -> None:
        # The linked user has the add_task permission but the key's API level is VIEW (1),
        # which is below the ADD (2) level the create endpoint requires.
        raw_key, _user = self.create_user_key('adder', 'add_task', ApiPermissionChoices.VIEW)

        payload = {'name': 'New Task'}
        response = self.post_json(self.list_url(), payload, {'HTTP_X_API_KEY': raw_key})

        assert response.status_code == 401
        assert not Task.objects.filter(name='New Task').exists()

    def test_create_task_creates_task(self) -> None:
        payload = {'name': 'New Task', 'description': 'A description'}
        response = self.post_json(self.list_url(), payload, self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert body['name'] == 'New Task'
        assert body['description'] == 'A description'
        assert body['status'] == TaskStatusChoices.NEW
        assert body['is_deleted'] is False
        assert Task.objects.filter(pk=body['id'], name='New Task').exists()

    def test_create_task_links_parent(self) -> None:
        payload = {'name': 'Sub Task', 'parent_id': self.parent_task.id}
        response = self.post_json(self.list_url(), payload, self.api_extra())

        assert response.status_code == 200
        assert response.json()['parent_id'] == self.parent_task.id

    def test_create_task_missing_name_is_invalid(self) -> None:
        response = self.post_json(self.list_url(), {'description': 'no name'}, self.api_extra())

        assert response.status_code == 422
        assert Task.objects.count() == 3

    def test_create_task_over_max_name_length_is_invalid(self) -> None:
        response = self.post_json(self.list_url(), {'name': 'x' * 256}, self.api_extra())

        assert response.status_code == 422


class TaskDetailApiTestCase(TaskApiTestCase):
    def test_detail_returns_task(self) -> None:
        response = self.client.get(self.detail_url(self.parent_task.id), **self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert body['id'] == self.parent_task.id
        assert body['name'] == 'Parent Task'

    def test_detail_unknown_task_returns_404(self) -> None:
        response = self.client.get(self.detail_url(99999), **self.api_extra())

        assert response.status_code == 404

    def test_detail_deleted_task_returns_404(self) -> None:
        self.parent_task.set_deleted()

        response = self.client.get(self.detail_url(self.parent_task.id), **self.api_extra())

        assert response.status_code == 404


class UpdateTaskApiTestCase(TaskApiTestCase):
    def test_update_task_changes_fields(self) -> None:
        payload = {'name': 'Updated Name', 'description': 'Updated description'}
        response = self.client.put(
            self.detail_url(self.parent_task.id),
            data=json.dumps(payload),
            content_type='application/json',
            **self.api_extra(),
        )

        assert response.status_code == 200
        body = response.json()
        assert body['name'] == 'Updated Name'
        assert body['description'] == 'Updated description'
        assert body['status'] == TaskStatusChoices.NEW

    def test_update_task_partial_keeps_other_fields(self) -> None:
        payload = {'status': TaskStatusChoices.IN_PROGRESS}
        response = self.client.put(
            self.detail_url(self.parent_task.id),
            data=json.dumps(payload),
            content_type='application/json',
            **self.api_extra(),
        )

        assert response.status_code == 200
        body = response.json()
        assert body['name'] == 'Parent Task'
        assert body['status'] == TaskStatusChoices.IN_PROGRESS

    def test_update_task_reparents(self) -> None:
        payload = {'parent_id': self.parent_task.id}
        response = self.client.put(
            self.detail_url(self.done_task.id),
            data=json.dumps(payload),
            content_type='application/json',
            **self.api_extra(),
        )

        assert response.status_code == 200
        assert response.json()['parent_id'] == self.parent_task.id

    def test_update_deleted_task_returns_404(self) -> None:
        self.child_task.set_deleted()

        payload = {'name': 'Nope'}
        response = self.client.put(
            self.detail_url(self.child_task.id),
            data=json.dumps(payload),
            content_type='application/json',
            **self.api_extra(),
        )

        assert response.status_code == 404


class DeleteTaskApiTestCase(TaskApiTestCase):
    def test_delete_task_soft_deletes(self) -> None:
        response = self.client.delete(self.detail_url(self.parent_task.id), **self.api_extra())

        assert response.status_code == 200
        assert response.json() == {'deleted': True, 'id': self.parent_task.id}
        self.parent_task.refresh_from_db()
        assert self.parent_task.is_deleted is True

    def test_delete_task_removes_from_list(self) -> None:
        self.client.delete(self.detail_url(self.parent_task.id), **self.api_extra())

        response = self.client.get(self.list_url(), **self.api_extra())
        assert response.json()['count'] == 2

    def test_delete_deleted_task_returns_404(self) -> None:
        self.parent_task.set_deleted()

        response = self.client.delete(self.detail_url(self.parent_task.id), **self.api_extra())

        assert response.status_code == 404


class CompleteTaskApiTestCase(TaskApiTestCase):
    def test_complete_sets_status_done(self) -> None:
        response = self.client.post(self.complete_url(self.parent_task.id), **self.api_extra())

        assert response.status_code == 200
        assert response.json()['status'] == TaskStatusChoices.DONE
        self.parent_task.refresh_from_db()
        assert self.parent_task.status == TaskStatusChoices.DONE

    def test_complete_deleted_task_returns_404(self) -> None:
        self.parent_task.set_deleted()

        response = self.client.post(self.complete_url(self.parent_task.id), **self.api_extra())

        assert response.status_code == 404


class TaskUsersApiTestCase(TaskApiTestCase):
    def test_list_task_users_empty(self) -> None:
        response = self.client.get(self.users_url(self.parent_task.id), **self.api_extra())

        assert response.status_code == 200
        assert response.json() == []

    def test_add_and_list_task_users(self) -> None:
        payload = {'user_id': self.worker_user.id, 'role': TaskUserRoleChoices.SUPPORT}
        response = self.post_json(self.users_url(self.parent_task.id), payload, self.api_extra())

        assert response.status_code == 200
        body = response.json()
        assert body['user_id'] == self.worker_user.id
        assert body['user_name'] == 'Jo Smith'
        assert body['role'] == TaskUserRoleChoices.SUPPORT

        response = self.client.get(self.users_url(self.parent_task.id), **self.api_extra())
        assert len(response.json()) == 1

    def test_add_task_user_updates_existing_role(self) -> None:
        task_user = TaskUser.objects.create(
            task=self.parent_task, user=self.worker_user, role=TaskUserRoleChoices.LEADER
        )

        payload = {'user_id': self.worker_user.id, 'role': TaskUserRoleChoices.FOLLOWER}
        response = self.post_json(self.users_url(self.parent_task.id), payload, self.api_extra())

        assert response.status_code == 200
        assert response.json()['role'] == TaskUserRoleChoices.FOLLOWER
        assert TaskUser.objects.filter(pk=task_user.pk).count() == 1

    def test_add_task_user_unknown_user_returns_404(self) -> None:
        payload = {'user_id': 99999}
        response = self.post_json(self.users_url(self.parent_task.id), payload, self.api_extra())

        assert response.status_code == 404

    def test_remove_task_user_soft_deletes(self) -> None:
        task_user = TaskUser.objects.create(
            task=self.parent_task, user=self.worker_user, role=TaskUserRoleChoices.LEADER
        )
        url = reverse(
            f'{BASE_URL_NAME}:api_v1:remove_task_user',
            kwargs={'task_id': self.parent_task.id, 'task_user_id': task_user.id},
        )

        response = self.client.delete(url, **self.api_extra())

        assert response.status_code == 200
        assert response.json() == {'deleted': True, 'id': task_user.id}
        task_user.refresh_from_db()
        assert task_user.is_deleted is True

    def test_remove_task_user_unknown_returns_404(self) -> None:
        url = reverse(
            f'{BASE_URL_NAME}:api_v1:remove_task_user',
            kwargs={'task_id': self.parent_task.id, 'task_user_id': 99999},
        )

        response = self.client.delete(url, **self.api_extra())

        assert response.status_code == 404


class TaskMembershipApiTestCase(TaskApiTestCase):
    def setUp(self) -> None:
        super().setUp()

        self.member_key, self.member_user = self.create_user_key(
            'member', ['add_task', 'change_task', 'delete_task'], ApiPermissionChoices.DELETE
        )
        self.outsider_key, _outsider_user = self.create_user_key(
            'outsider', ['add_task', 'change_task', 'delete_task'], ApiPermissionChoices.DELETE
        )

        self.member_task = self.create_task(name='Member Task')
        TaskUser.objects.create(task=self.member_task, user=self.member_user)

    def member_extra(self) -> dict:
        return {'HTTP_X_API_KEY': self.member_key}

    def outsider_extra(self) -> dict:
        return {'HTTP_X_API_KEY': self.outsider_key}

    def test_member_can_update_task(self) -> None:
        payload = {'name': 'Updated By Member'}
        response = self.client.put(
            self.detail_url(self.member_task.id),
            data=json.dumps(payload),
            content_type='application/json',
            **self.member_extra(),
        )

        assert response.status_code == 200
        assert response.json()['name'] == 'Updated By Member'

    def test_non_member_cannot_update_task(self) -> None:
        payload = {'name': 'Hijacked'}
        response = self.client.put(
            self.detail_url(self.member_task.id),
            data=json.dumps(payload),
            content_type='application/json',
            **self.outsider_extra(),
        )

        assert response.status_code == 403
        self.member_task.refresh_from_db()
        assert self.member_task.name == 'Member Task'

    def test_member_can_complete_task(self) -> None:
        response = self.client.post(self.complete_url(self.member_task.id), **self.member_extra())

        assert response.status_code == 200
        assert response.json()['status'] == TaskStatusChoices.DONE

    def test_non_member_cannot_complete_task(self) -> None:
        response = self.client.post(self.complete_url(self.member_task.id), **self.outsider_extra())

        assert response.status_code == 403
        self.member_task.refresh_from_db()
        assert self.member_task.status == TaskStatusChoices.NEW

    def test_member_can_delete_task(self) -> None:
        response = self.client.delete(self.detail_url(self.member_task.id), **self.member_extra())

        assert response.status_code == 200
        self.member_task.refresh_from_db()
        assert self.member_task.is_deleted is True

    def test_non_member_cannot_delete_task(self) -> None:
        response = self.client.delete(self.detail_url(self.member_task.id), **self.outsider_extra())

        assert response.status_code == 403
        self.member_task.refresh_from_db()
        assert self.member_task.is_deleted is False

    def test_member_can_add_task_user(self) -> None:
        payload = {'user_id': self.worker_user.id, 'role': TaskUserRoleChoices.SUPPORT}
        response = self.post_json(self.users_url(self.member_task.id), payload, self.member_extra())

        assert response.status_code == 200
        assert response.json()['user_id'] == self.worker_user.id

    def test_non_member_cannot_add_task_user(self) -> None:
        payload = {'user_id': self.worker_user.id}
        response = self.post_json(
            self.users_url(self.member_task.id), payload, self.outsider_extra()
        )

        assert response.status_code == 403

    def test_member_can_remove_task_user(self) -> None:
        task_user = TaskUser.objects.create(task=self.member_task, user=self.worker_user)
        url = reverse(
            f'{BASE_URL_NAME}:api_v1:remove_task_user',
            kwargs={'task_id': self.member_task.id, 'task_user_id': task_user.id},
        )

        response = self.client.delete(url, **self.member_extra())

        assert response.status_code == 200
        task_user.refresh_from_db()
        assert task_user.is_deleted is True

    def test_non_member_cannot_remove_task_user(self) -> None:
        task_user = TaskUser.objects.create(task=self.member_task, user=self.worker_user)
        url = reverse(
            f'{BASE_URL_NAME}:api_v1:remove_task_user',
            kwargs={'task_id': self.member_task.id, 'task_user_id': task_user.id},
        )

        response = self.client.delete(url, **self.outsider_extra())

        assert response.status_code == 403
        task_user.refresh_from_db()
        assert task_user.is_deleted is False

    def test_super_access_can_change_non_member_task(self) -> None:
        payload = {'name': 'Admin Override'}
        response = self.client.put(
            self.detail_url(self.member_task.id),
            data=json.dumps(payload),
            content_type='application/json',
            **self.api_extra(),
        )

        assert response.status_code == 200
        assert response.json()['name'] == 'Admin Override'

    def test_creator_becomes_a_member(self) -> None:
        payload = {'name': 'Created By Member'}
        response = self.post_json(self.list_url(), payload, self.member_extra())

        assert response.status_code == 200
        task = Task.objects.get(pk=response.json()['id'])
        assert TaskUser.objects.filter(task=task, user=self.member_user, is_deleted=False).exists()
