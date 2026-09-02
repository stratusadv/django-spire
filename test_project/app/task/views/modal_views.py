from django.http.request import HttpRequest
from django.template.response import TemplateResponse
from django_glue import Glue

from django_spire.contrib.shortcuts import get_object_or_null_obj
from test_project.app.task import forms, models


def form_view(request: HttpRequest, pk: int = 0):
    task = get_object_or_null_obj(models.Task, pk=pk)

    form = forms.TaskModelForm(request.POST or None, instance=task)

    Glue.form(request, 'task_form', form, Glue.Access.CHANGE)

    return TemplateResponse(
        request, template='task/modal/content/task_form_modal_content.html'
    )