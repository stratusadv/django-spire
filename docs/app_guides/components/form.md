# Form Components

> **Purpose:** Show one Django form as a Glue component, so the same form can be opened in a modal, placed on a page, or handed to a list to create and edit its rows.

---

## Why Form Components?

A form shown in a modal needs its fields, its values, its validation and its save to reach the browser together. **The form components** provide:

- A component around a `Form` or a `ModelForm`, with the form as its Glue child
- Create and edit from one component: no primary key creates, a primary key edits
- A component built straight from a form class and a template, with no subclass
- Hooks for choosing the row, the exposed fields and the choices of relation fields
- A path to the form that templates read, so a form partial works wherever it is included
- Options that tell a [scroll component](scroll.md) to use a form component or a form page

---

## Quick Start

### 1. Give the form a save the browser can call

```python
from django.forms import ModelForm
from django_glue import Glue, GlueResponse
from django_glue.message import GlueMessage

from app.task.models import Task


class TaskForm(ModelForm):
    saved = Glue.event()

    @Glue.attr(required_access=Glue.Access.required_save_access)
    def save_model_obj(self) -> GlueResponse:
        if not self.is_valid():
            return GlueResponse(messages=[GlueMessage.error('Invalid Fields')])

        task, _created = self.instance.services.save_model_obj(**self.cleaned_data)
        self.saved(pk=task.pk)

        return GlueResponse(result={'pk': task.pk})

    class Meta:
        model = Task
        fields = ['name', 'status']
```

### 2. Write the form's templates

The fields, in `task/form/task_form.html`:

```html
--8<-- "docs/app_guides/components/templates/form_task_modal.html"
```

The modal content around them, in `task/modal/content/task_form_modal_content.html`:

```html
--8<-- "docs/app_guides/components/templates/form_task_modal_content.html"
```

The component's own template, in `task/component/task_form_modal.html`:

```html
--8<-- "docs/app_guides/components/templates/form_task_component.html"
```

### 3. Give the form to a list

```python
from django_spire.core.components import ComponentFormOptions, ModelCrudScrollComponent


class TaskListComponent(ModelCrudScrollComponent):
    item_form_options = ComponentFormOptions(
        form_class=TaskForm,
        template='task/component/task_form_modal.html',
    )
```

The list's New and Edit buttons now open the form in a modal, and a saved row appears or updates in the list.

---

## Core Concepts

### `ModelFormComponent`

A component around a `ModelForm`. The row is its `model` child, a Glue model, and the form hangs off that at `component.model.form`.

```python
from django_spire.core.components import ModelFormComponent
```

| Member | Description |
|---|---|
| `form_class` | The `ModelForm` class. The model is the form's own |
| `template` | The component's template |
| `pk` | A parameter. `None` creates a row, a value edits that row |
| `fields` | The fields the Glue model exposes. Defaults to the form's fields |
| `get_model()` | Return the row. A blank one, or the row with `pk`, by default |
| `get_fields()` | Return the exposed fields |
| `get_choices(instance)` | Return a dict of choice querysets for relation fields. `None` by default |

A row that no longer exists is reported as Glue's `model_instance_not_found`, a 404.

### `FormComponent`

A component around a plain `Form`, for a form that is not tied to a row. The form is its `form` child, at `component.form`.

```python
from django_spire.core.components import FormComponent
```

| Member | Description |
|---|---|
| `form_class` | The `Form` class |
| `template` | The component's template |
| `get_form()` | Return the form. Override it when the form needs constructor arguments |

### `BaseFormComponent`

The parent of both. It resolves the form class and the template, however they were given, and declares `glue_form_path()`.

```python
from django_spire.core.components import BaseFormComponent
```

`glue_form_path()` returns the path from the template to the form: `component.model.form` or `component.form`. A form partial reads it as `component.glue_form_path`, and `django_spire/glue/form/modal_form.html` uses it by default, so the same partial works under either component.

### `ComponentFormOptions` and `PageFormOptions`

Tell a CRUD scroll how its rows are created and edited.

```python
from django_spire.core.components import ComponentFormOptions, PageFormOptions
```

| Options | Arguments | Description |
|---|---|---|
| `ComponentFormOptions` | `component` | The application's own form component class |
| `ComponentFormOptions` | `form_class`, `template` | A form class and a template, shown by `ModelFormComponent` itself |
| `PageFormOptions` | `url_name`, `create_url_name`, `return_url_name` | A form page. `url_name` takes the row's key as `pk` |

`ComponentFormOptions` takes a component, or a form class together with a template, and refuses any other combination when it is created.

---

## Main Operations

### Building a Form Component Without a Subclass

```python
form = ModelFormComponent(
    form_class=TaskForm,
    template='task/component/task_form_modal.html',
    pk=task.pk,
)
```

The form class is carried to the browser as its import path, so it must be defined at the top level of a module. A form class defined inside a function is refused.

### Writing a Form Component Class

```python
class TaskFormComponent(ModelFormComponent):
    template = 'task/component/task_form_modal.html'
    form_class = TaskForm
```

Write a class when the component needs hooks of its own, or parameters beyond `pk`.

### Opening a Form From a Callable

```python
from django_glue import Glue


class TaskBoardComponent(Glue.Component):
    template = 'task/component/task_board.html'

    @Glue.attr(required_access=Glue.Access.CHANGE)
    def task_form(self, pk: int | None = None) -> TaskFormComponent:
        return TaskFormComponent(pk=pk, access=self.access)
```

```html
--8<-- "docs/app_guides/components/templates/form_open_in_modal.html"
```

The callable returns the form component and the page shows it. The form component closes nothing itself: the page listens for the form's `saved` event and closes the modal.

### Scoping or Pre-filling the Row

```python
class TaskFormComponent(ModelFormComponent):
    template = 'task/component/task_form_modal.html'
    form_class = TaskForm

    def get_model(self) -> Task:
        if self.pk is None:
            return Task(assigned_to=self.request.user)

        return Task.objects.active().get(pk=self.pk, assigned_to=self.request.user)
```

`get_model()` picks the row. Override it to give a new row its defaults, or to limit which rows the component will open. The default looks a row up by primary key with no other condition.

### Exposing Fewer Fields

```python
class TaskFormComponent(ModelFormComponent):
    template = 'task/component/task_form_modal.html'
    form_class = TaskForm
    fields = ('name',)
```

`fields` narrows what the Glue model exposes to the browser. Override `get_fields()` when it depends on the request.

### Supplying Choices for a Relation Field

```python
class TaskFormComponent(ModelFormComponent):
    template = 'task/component/task_form_modal.html'
    form_class = TaskForm

    def get_choices(self, instance: Task) -> dict:
        return {'project': Project.objects.active().filter(team=instance.team)}
```

`get_choices()` receives the row and returns the querysets a relation field may choose from.

---

## Upgrading From 1.2

The form components were reworked in 1.3.0. A subclass that still uses a removed name raises `TypeError` when it is defined, naming the replacement.

| In 1.2 | In 1.3 |
|---|---|
| `from django_spire.core.glue.components import ...` | `from django_spire.core.components import ...` |
| `form = TaskForm` | `form_class = TaskForm` |
| `attr = 'time_entry'` | Removed. The child is always `model` on a `ModelFormComponent` and `form` on a `FormComponent` |
| `component.time_entry.form` in a template | `component.model.form`, or better, `component.glue_form_path` |
| `model_class = Task` | Removed. The model is the form's own |
| `fields = (...)`, required | Optional. Defaults to the form's fields |
| `build_child()` | Removed. Override `get_form()`, or the hooks on `ModelFormComponent` |
| `ModelFormComponent` inherits from `FormComponent` | Both inherit from `BaseFormComponent` |

A template that reads the form through `component.glue_form_path`, or that extends `modal_form.html`, needs no change.
