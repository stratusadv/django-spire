from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.timezone import localtime

from django_spire.auth.group.models import AuthGroup
from django_spire.history.activity.context import activity_user
from django_spire.history.activity.models import Activity

from test_project.app.task.models import Task

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.db.models import QuerySet


DEMO_EXTRA_MEMBER_COUNT = 3
DEMO_GROUP_NAME = 'Activity Demo Group'
DEMO_MEMBER_PREFIX = 'activity_demo_'
DEMO_MEMBER_USERNAME = 'activity_demo_member'
DEMO_TASK_PREFIX = 'Activity Demo Task'
FEED_COUNT_MAX = 30


def _demo_tasks() -> QuerySet[Task]:
    return Task.objects.filter(name__startswith=DEMO_TASK_PREFIX)


def _next_task_name() -> str:
    return f'{DEMO_TASK_PREFIX} {_demo_tasks().count() + 1}'


def _demo_group() -> AuthGroup:
    group, _ = AuthGroup.objects.get_or_create(name=DEMO_GROUP_NAME)
    return group


def _demo_member() -> User:
    defaults = {'first_name': 'Demo', 'last_name': 'Member'}
    member, _ = User.objects.get_or_create(username=DEMO_MEMBER_USERNAME, defaults=defaults)
    return member


def _demo_extra_members() -> list[User]:
    members = []

    for index in range(1, DEMO_EXTRA_MEMBER_COUNT + 1):
        defaults = {'first_name': 'Extra', 'last_name': f'Member {index}'}

        member, _ = User.objects.get_or_create(
            username=f'{DEMO_MEMBER_PREFIX}extra_{index}',
            defaults=defaults,
        )

        members.append(member)

    return members


def _redirect_to_demo() -> HttpResponseRedirect:
    return HttpResponseRedirect(reverse('activity:demo'))


@login_required()
def demo_view(request: WSGIRequest) -> TemplateResponse:
    demo_tasks = _demo_tasks()
    group = AuthGroup.objects.filter(name=DEMO_GROUP_NAME).first()
    member = User.objects.filter(username=DEMO_MEMBER_USERNAME).first()

    member_in_group = bool(
        group is not None
        and member is not None
        and group.user_set.filter(pk=member.pk).exists()
    )

    context_data = {
        'activities': Activity.objects.prefetch_user()[:FEED_COUNT_MAX],
        'activity_count': Activity.objects.count(),
        'group_member_count': group.user_set.count() if group is not None else 0,
        'member_in_group': member_in_group,
        'task_count': demo_tasks.count(),
        'task_deleted_count': demo_tasks.deleted().count(),
        'page_title': 'Activity Demo',
        'page_description': 'Event-Based Activity Walkthrough',
        'breadcrumbs': [{'name': 'Activity Demo', 'href': None}],
    }

    return TemplateResponse(
        request, context=context_data, template='activity/page/activity_demo_page.html'
    )


@login_required()
def create_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        Task.objects.create(name=_next_task_name())

    return _redirect_to_demo()


@login_required()
def child_create_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        parent = _demo_tasks().not_deleted().order_by('pk').first()

        if parent is not None:
            Task.objects.create(name=_next_task_name(), parent=parent)

    return _redirect_to_demo()


@login_required()
def unattributed_create_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        with activity_user(None):
            Task.objects.create(name=_next_task_name())

    return _redirect_to_demo()


@login_required()
def update_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        task = _demo_tasks().not_deleted().order_by('-pk').first()

        if task is not None:
            task.description = f'Updated at {localtime():%H:%M:%S}'
            task.save()

    return _redirect_to_demo()


@login_required()
def soft_delete_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        task = _demo_tasks().not_deleted().order_by('pk').first()

        if task is not None:
            task.set_deleted()

    return _redirect_to_demo()


@login_required()
def restore_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        task = _demo_tasks().deleted().order_by('pk').first()

        if task is not None:
            task.un_set_deleted()

    return _redirect_to_demo()


@login_required()
def hard_delete_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        task = _demo_tasks().order_by('-pk').first()

        if task is not None:
            task.delete()

    return _redirect_to_demo()


@login_required()
def cascade_delete_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        task = _demo_tasks().filter(parent__isnull=True).order_by('pk').first()

        if task is not None:
            task.delete()

    return _redirect_to_demo()


@login_required()
def bulk_create_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        start_count = _demo_tasks().count()

        tasks = [
            Task(name=f'{DEMO_TASK_PREFIX} {start_count + offset}')
            for offset in range(1, 4)
        ]

        Task.objects.bulk_create(tasks)

    return _redirect_to_demo()


@login_required()
def bulk_update_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        tasks = list(_demo_tasks().order_by('-pk')[:3])

        for task in tasks:
            task.description = f'Bulk updated at {localtime():%H:%M:%S}'

        if tasks:
            Task.objects.bulk_update(tasks, ['description'])

    return _redirect_to_demo()


@login_required()
def queryset_update_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        _demo_tasks().update(description=f'Queryset updated at {localtime():%H:%M:%S}')

    return _redirect_to_demo()


@login_required()
def queryset_delete_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        pks = list(_demo_tasks().order_by('-pk').values_list('pk', flat=True)[:3])
        _demo_tasks().filter(pk__in=pks).delete()

    return _redirect_to_demo()


@login_required()
def member_add_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        _demo_group().user_set.add(_demo_member())

    return _redirect_to_demo()


@login_required()
def member_add_many_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        _demo_group().user_set.add(*_demo_extra_members())

    return _redirect_to_demo()


@login_required()
def member_remove_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        group = AuthGroup.objects.filter(name=DEMO_GROUP_NAME).first()
        member = User.objects.filter(username=DEMO_MEMBER_USERNAME).first()

        if group is not None and member is not None:
            group.user_set.remove(member)

    return _redirect_to_demo()


@login_required()
def member_clear_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        group = AuthGroup.objects.filter(name=DEMO_GROUP_NAME).first()

        if group is not None:
            group.user_set.clear()

    return _redirect_to_demo()


@login_required()
def reset_view(request: WSGIRequest) -> HttpResponseRedirect:
    if request.method == 'POST':
        _demo_tasks().delete()
        AuthGroup.objects.filter(name=DEMO_GROUP_NAME).delete()
        User.objects.filter(username__startswith=DEMO_MEMBER_PREFIX).delete()
        Activity.objects.all().delete()

    return _redirect_to_demo()
