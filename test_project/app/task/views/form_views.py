from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse

from django_glue import Glue

from django_spire.contrib.form.tools import show_form_errors
from django_spire.contrib.redirects import safe_redirect_url
from django_spire.contrib.shortcuts import get_object_or_null_obj

from test_project.app.task import forms, models
from test_project.app.task.navigation import TaskNavigation

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest


def glue_form_view(request: WSGIRequest, pk: int) -> TemplateResponse | redirect:
    task = get_object_or_null_obj(models.Task, pk=pk)

    nav = TaskNavigation()
    nav.set_page_title_from_model_instance_form_action(task)
    nav.breadcrumbs.add(f'{task.name}' if task.pk else 'New Task (With Glue)')

    form = forms.TaskGlueModelForm(request.POST or None, instance=task)

    Glue.form(request, 'task_model_form', form, Glue.Access.DELETE)

    context = {**nav.as_context()}

    return TemplateResponse(
        request=request, context=context, template='task/page/glue_form_page.html'
    )


def create_view(request: WSGIRequest) -> TemplateResponse | redirect:
    task = models.Task()

    return _form_view(request, task)


def update_view(request: WSGIRequest, pk: int) -> TemplateResponse | redirect:
    task = get_object_or_404(models.Task, pk=pk)

    return _form_view(request, task)


def _form_view(request: WSGIRequest, task: models.Task) -> TemplateResponse | redirect:
    if request.method == 'POST':
        form = forms.TaskModelForm(request.POST, instance=task)

        if form.is_valid():
            task.services.save_model_obj(user=request.user, obj=task, **form.cleaned_data)

            return redirect(request.GET.get('return_url', reverse('task:page:list')))

        show_form_errors(request, form)
    else:
        form = forms.TaskModelForm(instance=task)

    nav = TaskNavigation()
    nav.set_page_title_from_model_instance_form_action(task)
    nav.breadcrumbs.add(f'{task.name}' if task.pk else 'New Task')

    context = nav.as_context()
    context['form'] = form
    context['task'] = task

    return TemplateResponse(request=request, context=context, template='task/page/form_page.html')


def delete_view(request: WSGIRequest, pk: int) -> TemplateResponse | redirect:
    task = get_object_or_404(models.Task, pk=pk)

    return_url = request.GET.get('return_url', reverse('task:page:list'))

    if request.method == 'POST':
        task.set_deleted()

        task.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted task {task.name}.',
        )

        return redirect(return_url)

    nav = TaskNavigation()
    nav.page_title = f'Delete {task.name}'
    nav.breadcrumbs.add('Tasks', 'task:page:list')
    nav.breadcrumbs.add(f'Delete {task.name}')

    context = nav.as_context()
    context['task'] = task
    context['return_url'] = return_url

    return TemplateResponse(request=request, context=context, template='task/page/delete_page.html')


def create_modal_view(request: WSGIRequest) -> TemplateResponse:
    return _modal_form_view(request)


def update_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    return _modal_form_view(request, pk)


def _modal_form_view(request: WSGIRequest, pk: int = 0) -> TemplateResponse:
    task = get_object_or_null_obj(models.Task, pk=pk)

    Glue.model(request, 'task', task)

    context = {'task': task}

    return TemplateResponse(
        request, context=context, template='task/modal/content/task_modal_content.html'
    )


def delete_modal_view(request: WSGIRequest, pk: int) -> TemplateResponse:
    task = get_object_or_404(models.Task, pk=pk)

    return_url = safe_redirect_url(request, fallback=reverse('task:page:list'))

    if request.method == 'POST':
        task.set_deleted()

        task.add_activity(
            user=request.user,
            verb='deleted',
            information=f'{request.user.get_full_name()} deleted task {task.name}.',
        )

        return redirect(return_url)

    context = {
        'task': task,
        'form_action': reverse('task:form:delete_modal', kwargs={'pk': pk}),
        'return_url': return_url,
    }

    return TemplateResponse(
        request, context=context, template='task/modal/content/delete_modal_content.html'
    )
