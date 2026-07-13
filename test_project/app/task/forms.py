from django.forms import ModelForm
from django.http import HttpRequest
from django.urls import reverse
from django_glue import GlueResponse, Glue
from django_glue.message import GlueMessage

from test_project.app.task.models import Task


class TaskModelForm(ModelForm):
    @Glue.attribute(Glue.Access.CHANGE)
    def save_model_obj(self, request: HttpRequest, time_of_day: str | None = None) -> GlueResponse:
        if self.is_valid():
            task = Task.services.save_model_obj(request.user, **self.cleaned_data)

            return GlueResponse(
                result={'redirect_url': reverse('task:page:detail', kwargs={'pk': task.pk})}
            )

        return GlueResponse(
            messages=[
                GlueMessage(
                    GlueMessage.Level.ERROR,
                    'HELLO WORLD!'
                )
            ]
        )

    class Meta:
        model = Task
        fields = ['name', 'description', 'status']
