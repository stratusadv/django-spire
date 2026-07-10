from django import forms
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.urls import reverse
from django_glue.form.form import GlueModelForm
from django_glue.response import GlueJsonResponse

from test_project.app.task.choices import TaskStatusChoices
from test_project.app.task.models import Task


class TaskModelForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'status']


class TaskGlueModelForm(GlueModelForm):
    def process(self, request: WSGIRequest, payload: dict) -> GlueJsonResponse:
        if self.is_valid():
            task = Task.objects.create(**self.cleaned_data)

            return GlueJsonResponse(
                payload={'redirect_url': reverse('task:page:detail', kwargs={'pk': task.pk})}
            )

    class Meta:
        model = Task
        fields = ['name', 'description', 'status']


class TaskListFilterForm(forms.Form):
    name = forms.CharField(required=False)
    status = forms.ChoiceField(required=False, choices=TaskStatusChoices.choices)
    users = forms.ModelMultipleChoiceField(required=False, queryset=User.objects)
    search = forms.CharField(required=False)

    def clean_users(self):
        return [user.id for user in self.cleaned_data['users']]
