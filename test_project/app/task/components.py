from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django_glue import Glue

from django_spire.core.components import (
    ComponentItemFormOptions,
    GlueScrollItemsMixin,
    ModelCrudScrollComponent,
    ModelFormComponent,
)
from test_project.app.task.choices import TaskStatusChoices
from test_project.app.task.forms import TaskModalForm
from test_project.app.task.models import Task
from test_project.app.task.navigation import TaskNavigation

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest
    from django_glue.glue.objects.django.model.object import ModelGlue


ORDERINGS = {
    'name': 'Name',
    '-name': 'Name, descending',
    'status': 'Status',
    '-created_datetime': 'Newest first',
}


class TaskListComponent(GlueScrollItemsMixin, ModelCrudScrollComponent):
    template = 'task/component/task_list.html'
    view_template = 'task/page/task_list_page.html'
    fields = ('name', 'status')

    item_form_options = ComponentItemFormOptions(
        form_class=TaskModalForm,
        template='task/component/task_form_modal.html',
    )

    ordering_choices = tuple(ORDERINGS.items())
    status_choices = tuple(TaskStatusChoices.choices)

    search: str = Glue.attr('', editable=True)
    status: str = Glue.attr('', editable=True)
    ordering: str = Glue.attr('name', editable=True)

    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)

        self.access = Glue.Access.DELETE

        nav = TaskNavigation()
        nav.page_title = 'Task List Component'
        nav.breadcrumbs.add('List Component')
        self.context_data.update(nav.as_context())

    def get_queryset(self) -> QuerySet[Task]:
        queryset = Task.objects.active().top_level().annotate_has_children().search(self.search)

        if self.status in TaskStatusChoices.values:
            queryset = queryset.filter(status=self.status)

        return queryset.order_by(self.ordering if self.ordering in ORDERINGS else 'name')

    def get_glue_item(self, item: Task, name: str, **kwargs: Any) -> ModelGlue:
        return super().get_glue_item(item, name, form=TaskModalForm, **kwargs)

    @Glue.attr
    def child_list(self, pk: int) -> TaskChildListComponent:
        return TaskChildListComponent(parent_id=pk, access=self.access)


class TaskFormComponent(ModelFormComponent):
    template = 'task/component/task_form_modal.html'
    form_class = TaskModalForm


class TaskChildListComponent(TaskListComponent):
    template = 'task/component/task_child_list.html'
    batch_size = 10

    item_form_options = ComponentItemFormOptions(component=TaskFormComponent)

    parent_id: int = Glue.attr(parameter=True)

    def get_queryset(self) -> QuerySet[Task]:
        return (
            Task.objects.active()
            .filter(parent_id=self.parent_id)
            .annotate_has_children()
            .order_by('name')
        )

    @Glue.attr(required_access=Glue.Access.CHANGE, skip_rerender=True)
    def detach(self, pk: int) -> None:
        self.get_queryset().get(pk=pk).services.save_model_obj(parent=None)
        self.item_removed(key=pk)
