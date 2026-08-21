# Service Layer

> **Purpose:** give every domain model a predictable “service layer” so business rules live next to the data and are invoked as naturally as `Task.objects`.

---

## 1 · Why a Service Layer?

Django’s flexibility often scatters business logic across views, utils, managers, and helpers. A dedicated service layer fixes that by pinning every rule to the model that owns it. Each model exposes a `services` descriptor that:

* groups validation, persistence, and side‑effects in one place
* is easy to reach from anywhere the model is reached — `task.services.factory.duplicate(request)`
* keeps code modular and easy to test
* avoids circular‑import headaches through **future annotations** and `TYPE_CHECKING` guards

The example below uses a simple **Task** model from the reference project.

---

## 2 · What the `BaseDjangoModelService` Gives You

| Method | Purpose |
| --- | --- |
| `save_model_obj(**field_data)` | The core save method. Updates `self.obj` from the kwargs, saves, and handles M2M fields — atomically. |

`save_model_obj()` emulates Django’s `BaseModelForm.save()` as closely as possible:

1. `_set_non_m2m_fields` sets the given fields on `self.obj` (same logic as `django.forms.models.construct_instance`)
2. `self.obj.save()`
3. `_set_m2m_fields` sets M2M fields (same logic as `BaseModelForm._save_m2m()`)

Behaviours to know:

* it is wrapped in `@transaction.atomic`, so a failed save rolls everything back
* it performs **no validation** — data is assumed to have been validated upstream (e.g. by a form), matching how `BaseModelForm` treats `cleaned_data`
* it also saves attribute changes made directly on the instance, so `save_model_obj()` with no kwargs behaves like `Model.save()`
* foreign keys accept the `_id` alias — `save_model_obj(creator_id=42)`
* file-type fields are deferred until after the other fields so a callable `upload_to` can use them
* it returns `tuple[Model, bool]` — the saved object and whether it was created

```python
# Returns (saved_obj, was_created)
task, created = task.services.save_model_obj(name='New task', status='new')
```

---

## 3 · Building a `TaskService`

### 3.1 Files & Directories

One package per model, one file per service:

```
task/
├── models.py
└── services/
    ├── __init__.py
    ├── service.py              # TaskService (primary)
    ├── factory_service.py      # TaskFactoryService (create new objects)
    ├── processor_service.py    # TaskProcessorService (act on the object)
    └── transformation_service.py  # TaskTransformationService (turn it into something else)
```

### 3.2 The Model

```python
# task/models.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from task.services.service import TaskService


class Task(models.Model):
    name = models.CharField(max_length=200)
    is_done = models.BooleanField(default=False)

    services = TaskService()

    def __str__(self) -> str:
        return self.name
```

### 3.3 The Service (and sub‑services!)

```python
# task/services/service.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService
from task.services.factory_service import TaskFactoryService

if TYPE_CHECKING:
    from task.models import Task


class TaskService(BaseDjangoModelService['Task']):
    # target model — must be first
    obj: Task

    # followed by all sub services
    factory = TaskFactoryService()
```

```python
# task/services/factory_service.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from task.models import Task


class TaskFactoryService(BaseDjangoModelService['Task']):
    obj: Task

    def duplicate(self) -> Task:
        new_task, _ = self.obj_class.services.save_model_obj(
            name=f'{self.obj.name} (Copy)',
            is_done=False,
        )
        return new_task
```

Every class in the chain must annotate `obj` with the **same** target model; the constructor validates that and raises `ConstructorError` on mismatch.

---

## 4 · Common Service Files

| File path | Class | Responsibility |
| --- | --- | --- |
| `services/service.py` | `TaskService` | Parent service class that links sub services |
| `services/factory_service.py` | `TaskFactoryService` | Create new objects from an existing one |
| `services/processor_service.py` | `TaskProcessorService` | Perform actions on that object |
| `services/transformation_service.py` | `TaskTransformationService` | Turn the object into new forms of other objects |

Each secondary service begins with `obj: Task` so it plugs into the same descriptor system.

---

## 5 · Instance‑ vs Class‑Level Access

```python
from task.models import Task

# Instance‑level use – operate on one concrete record
task = Task.objects.get(pk=42)
copy = task.services.factory.duplicate()

# Class‑level use – no row yet, or act on many rows
# The descriptor fabricates a "null" Task (pk = None) behind the scenes,
# applies defaults, then runs the service logic.
Task.services.factory.clean_dead_tasks()
```

### When to pick which

| Use‑case | Call form | Why it makes sense |
| --- | --- | --- |
| Work on **one existing** row | `task.services.factory.duplicate()` | You already have the instance; the service mutates it and persists changes. |
| Run **bulk / maintenance** logic or logic **before** a row exists | `Task.services.factory.clean_dead_tasks()` | You need the behaviour but not a specific row to start from; the service works from a null instance. |

---

## 6 · Accessing the Model Class from a Service

You may need the model class itself to run queries from inside a service. The service exposes it as `self.obj_class`:

```python
# task/services/processor_service.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.constructor.service import BaseDjangoModelService

if TYPE_CHECKING:
    from task.models import Task


class TaskProcessorService(BaseDjangoModelService['Task']):
    obj: Task

    def mark_stale(self) -> list[Task]:
        stale_tasks = self.obj_class.objects.filter(is_done=False, created_datetime__lt='2020-01-01')
        return list(stale_tasks)
```

`obj_class` resolves to the model class for whatever instance the service is bound to, so it also works at class level.

---

## 7 · Exposing Services to Templates with Glue

Service methods can be bound straight into templates with `Glue.attr`:

```python
from django_glue import Glue
from task.services.factory_service import TaskFactoryService


class TaskService(BaseDjangoModelService['Task']):
    obj: Task

    factory = Glue.attr(TaskFactoryService(), required_access=Glue.Access.CHANGE)
```

```python
@Glue.attr(required_access=Glue.Access.CHANGE)
def duplicate(self, request) -> dict:
    ...
```

See the [Django Glue documentation](https://django-glue.stratusadv.com/) for the client side.
