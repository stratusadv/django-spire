from django import forms
from django.contrib.auth.models import User

from test_project.apps.queryset_filtering.choices import TaskStatusChoices
from test_project.apps.queryset_filtering.models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'status']


class TaskListFilterForm(forms.Form):
    name = forms.CharField(required=False)
    status = forms.ChoiceField(required=False, choices=TaskStatusChoices.choices)
    users = forms.ModelMultipleChoiceField(required=False, queryset=User.objects)
    search = forms.CharField(required=False)

    def clean_users(self):
        return [
            user.id for user in self.cleaned_data['users']
        ]
