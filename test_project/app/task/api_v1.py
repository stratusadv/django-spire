from __future__ import annotations

from django.contrib.auth.models import User
from django.http import Http404, HttpRequest
from ninja import ModelSchema, Query, Router, Schema
from ninja.errors import AuthorizationError

from django_spire.api.auth.security import ApiKeySecurity
from django_spire.api.choices import ApiPermissionChoices

from test_project.app.task.choices import TaskStatusChoices, TaskUserRoleChoices
from test_project.app.task.models import Task, TaskUser

view_auth = ApiKeySecurity(
    api_permission_required=ApiPermissionChoices.VIEW,
    user_permission_required='test_project_task.view_task',
)
add_auth = ApiKeySecurity(
    api_permission_required=ApiPermissionChoices.ADD,
    user_permission_required='test_project_task.add_task',
)
change_auth = ApiKeySecurity(
    api_permission_required=ApiPermissionChoices.CHANGE,
    user_permission_required='test_project_task.change_task',
)
delete_auth = ApiKeySecurity(
    api_permission_required=ApiPermissionChoices.DELETE,
    user_permission_required='test_project_task.delete_task',
)

router = Router()


class TaskIn(ModelSchema):
    class Meta:
        model = Task
        fields = ['name', 'description', 'status', 'parent']
        fields_optional = ['description', 'status', 'parent']


class TaskUpdateIn(ModelSchema):
    class Meta:
        model = Task
        fields = ['name', 'description', 'status', 'parent']
        fields_optional = '__all__'


class TaskOut(ModelSchema):
    class Meta:
        model = Task
        fields = [
            'id',
            'name',
            'description',
            'status',
            'parent',
            'created_datetime',
            'is_active',
            'is_deleted',
        ]


class TaskListOut(Schema):
    count: int
    results: list[TaskOut]


class TaskUserIn(Schema):
    user_id: int
    role: TaskUserRoleChoices = TaskUserRoleChoices.LEADER


class TaskUserOut(ModelSchema):
    class Meta:
        model = TaskUser
        fields = ['id', 'task', 'user', 'role']

    user_name: str

    @staticmethod
    def resolve_user_name(task_user: TaskUser) -> str:
        return task_user.user.get_full_name() or task_user.user.username


def _get_task(task_id: int, active_required: bool = False) -> Task:
    queryset = Task.objects.filter(pk=task_id, is_deleted=False)
    if active_required:
        queryset = queryset.active()

    task = queryset.first()
    if task is None:
        raise Http404

    return task


def _user_can_affect_task(request: HttpRequest, task: Task) -> bool:
    if request.auth.has_super_access:
        return True

    if not request.user.is_authenticated:
        return False

    return TaskUser.objects.filter(task=task, user=request.user, is_deleted=False).exists()


def _require_user_can_affect_task(request: HttpRequest, task: Task) -> None:
    if not _user_can_affect_task(request, task):
        raise AuthorizationError(message='You can only change tasks you belong to.')


@router.get('', auth=view_auth, response=TaskListOut, by_alias=True)
def list_tasks(
    request: HttpRequest,
    search: str | None = None,
    status: TaskStatusChoices | None = None,
    parent_id: int | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> TaskListOut:
    queryset = Task.objects.filter(is_deleted=False)

    if search:
        queryset = queryset.search(search)

    if status:
        queryset = queryset.filter(status=status)

    if parent_id is not None:
        queryset = queryset.filter(parent_id=parent_id)

    count = queryset.count()
    results = list(queryset[offset : offset + limit])

    return TaskListOut(count=count, results=results)


@router.post('', auth=add_auth, response=TaskOut, by_alias=True)
def create_task(request: HttpRequest, payload: TaskIn) -> TaskOut:
    task = Task()
    task, _created = task.services.save_model_obj(
        name=payload.name,
        description=payload.description,
        status=payload.status,
        parent_id=payload.parent,
    )

    if request.user.is_authenticated:
        TaskUser.objects.create(task=task, user=request.user)

    return task


@router.get('{task_id}', auth=view_auth, response=TaskOut, by_alias=True)
def task_detail(request: HttpRequest, task_id: int) -> TaskOut:
    return _get_task(task_id)


@router.put('{task_id}', auth=change_auth, response=TaskOut, by_alias=True)
def update_task(request: HttpRequest, task_id: int, payload: TaskUpdateIn) -> TaskOut:
    task = _get_task(task_id, active_required=True)

    _require_user_can_affect_task(request, task)

    task.services.save_model_obj(**payload.model_dump(exclude_unset=True, by_alias=True))

    return task


@router.delete('{task_id}', auth=delete_auth)
def delete_task(request: HttpRequest, task_id: int) -> dict:
    task = _get_task(task_id, active_required=True)

    _require_user_can_affect_task(request, task)

    task.set_deleted()

    return {'id': task_id, 'deleted': True}


@router.post('{task_id}/complete', auth=change_auth, response=TaskOut, by_alias=True)
def complete_task(request: HttpRequest, task_id: int) -> TaskOut:
    task = _get_task(task_id, active_required=True)

    _require_user_can_affect_task(request, task)

    task.services.save_model_obj(status=TaskStatusChoices.DONE)

    return task


@router.get('{task_id}/users', auth=view_auth, response=list[TaskUserOut], by_alias=True)
def list_task_users(request: HttpRequest, task_id: int) -> list[TaskUserOut]:
    task = _get_task(task_id)

    return list(task.users.filter(is_deleted=False))


@router.post('{task_id}/users', auth=add_auth, response=TaskUserOut, by_alias=True)
def add_task_user(request: HttpRequest, task_id: int, payload: TaskUserIn) -> TaskUserOut:
    task = _get_task(task_id, active_required=True)

    _require_user_can_affect_task(request, task)

    if not User.objects.filter(pk=payload.user_id).exists():
        raise Http404

    task_user, _created = TaskUser.objects.get_or_create(task=task, user_id=payload.user_id)
    task_user.role = payload.role
    task_user.save()

    return task_user


@router.delete('{task_id}/users/{task_user_id}', auth=delete_auth)
def remove_task_user(request: HttpRequest, task_id: int, task_user_id: int) -> dict:
    task = _get_task(task_id, active_required=True)

    _require_user_can_affect_task(request, task)

    task_user = TaskUser.objects.filter(pk=task_user_id, task_id=task_id, is_deleted=False).first()

    if task_user is None:
        raise Http404

    task_user.set_deleted()

    return {'id': task_user_id, 'deleted': True}
