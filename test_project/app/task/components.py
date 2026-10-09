from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django_glue import Glue

from django_spire.core.components import (
    ComponentFormOptions,
    GlueScrollItemsMixin,
    ModelCrudScrollComponent,
    ModelFormComponent,
    PageDeleteOptions,
)
from test_project.app.task.choices import TaskOrderingChoices, TaskStatusChoices
from test_project.app.task.forms import TaskModalForm
from test_project.app.task.models import Task
from test_project.app.task.navigation import TaskNavigation

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest
    from django_glue.glue.objects.django.model.object import ModelGlue


class TaskListComponent(GlueScrollItemsMixin, ModelCrudScrollComponent):
    template = 'task/component/task_list.html'
    item_template = 'task/item/task_row.html'
    view_template = 'django_spire/component/page/full_page.html'
    fields = ('name', 'status')

    item_form_options = ComponentFormOptions(
        form_class=TaskModalForm,
        template='task/component/task_form_modal.html',
    )

    done_status = TaskStatusChoices.DONE
    ordering_choices = tuple(TaskOrderingChoices.choices)
    status_choices = tuple(TaskStatusChoices.choices)

    search: str = Glue.attr('', editable=True)
    status: str = Glue.attr('', editable=True)
    ordering: str = Glue.attr(TaskOrderingChoices.NAME, editable=True)

    def __post_init__(self, request: HttpRequest) -> None:
        super().__post_init__(request)

        # Stands in for a permission check: a real list sets this from what the user may do.
        self.access = Glue.Access.DELETE

        nav = TaskNavigation()
        nav.page_title = 'Task List Component'
        nav.breadcrumbs.add('List Component')
        self.context_data.update(nav.as_context())

    def get_queryset(self) -> QuerySet[Task]:
        queryset = Task.objects.active().top_level().annotate_has_children().search(self.search)

        if self.status in TaskStatusChoices.values:
            queryset = queryset.filter(status=self.status)

        if self.ordering in TaskOrderingChoices.values:
            return queryset.order_by(self.ordering)

        return queryset.order_by(TaskOrderingChoices.NAME)

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

    item_delete_options = PageDeleteOptions('task:form:delete')
    item_form_options = ComponentFormOptions(component=TaskFormComponent)

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
        self.get_instance(pk).services.save_model_obj(parent=None)
        self.item_removed(key=pk)
