from django import forms

from test_project.apps.queryset_filtering.choices import TaskStatusChoices


class TaskListFilterForm(forms.Form):
    name = forms.CharField(required=False)
    status = forms.ChoiceField(required=False, choices=TaskStatusChoices.choices)
    search = forms.CharField(required=False)