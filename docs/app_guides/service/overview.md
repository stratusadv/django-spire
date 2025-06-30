# Service Layer

> **Purpose:** provide every domain model with a predictable “service layer” so business rules live next to data and are invoked as naturally as `Task.objects`.

---

## 1 · Why a Service Layer?

Django’s flexibility often scatters business logic across views, utils, managers, and helpers. A dedicated service layer fixes that by pinning every rule to the model that owns it. Each model exposes a `services` descriptor that:

* groups validation, persistence, and side‑effects in one place
* easy access from model `task.services.notification.send_created()`
* keeps code modular for easy testing
* avoids circular‑import headaches through **future annotations** and `TYPE_CHECKING` guards

The example below uses a simple **Task** model.

---

## 2 · What the `BaseService` Gives You

| Method                    | Purpose                                                                                                  |
| ------------------------- | -------------------------------------------------------------------------------------------------------- |
| `validate_model_obj()` | Runs `full_clean()` on the target object and raises if validation fails.                                 |
| `save_model_obj()`     | Calls `validate_model_obj()` and then `save()` | 


---

## 3 · Building a `TaskService`

### 3.1 Files & Directories

```
tasks/
├── models.py
└── services/
    ├── service.py              # TaskService (primary)
    └── notification_service.py  # TaskNotificationService (secondary)
```

### 3.2 The Model

```python
# tasks/models.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django.db import models

from app.tasks.services.service import TaskService

class Task(models.Model):
    title = models.CharField(max_length=200)
    is_done = models.BooleanField(default=False)
    
    services: TaskService = TaskService()

    def __str__(self) -> str:
        return self.title
```

### 3.3 The Service (and sub‑service!)

```python
# tasks/service/services.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from app.tasks.service.notification_service import TaskNotificationService
from app.tasks.service.processor_service import TaskProcessorService

if TYPE_CHECKING:
    from app.tasks.models import Task

class TaskService(BaseDjangoModelService):    
    # target model — must be first
    task: Task 

    # followed by all sub services
    notification: TaskNotificationService = TaskNotificationService()
    processor: TaskProcessorService = TaskProcessorService()
```

```python
# tasks/service/services.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task

class TaskProcessorService(BaseDjangoModelService):    
    task: Task 

    def mark_done(self) -> Task:
        self.task.is_done = True
        self.task.save()            
        return self.task
```

---

## 4 · Common Service Files

| File path                           | Class                       | Responsibility                               |
| ----------------------------------- | --------------------------- |----------------------------------------------|
| `service/services.py`               | `TaskService`               | Parent service class that links sub services |
| `service/notification_service.py`   | `TaskNotificationService`   | Deliver messages triggered by task events    |
| `service/transformation_service.py` | `TaskTransformationService` | Turn objects into new forms of other objects |
| `service/processor_service.py`      | `TaskProcessorService`      | Processes actions on that object             |

Each secondary service begins with `task: Task` so it plugs into the same descriptor system.

---

## 5 · Class‑ vs Instance‑Level Access

```python
from app.tasks.models import Task

# Instance‑level use – operate on one concrete record
task = Task.objects.get(pk=42)
after = task.services.mark_done()  

# Class‑level use – no row yet, or act on many rows
# The descriptor fabricates a "null" Task (pk = None) behind the scenes,
# applies defaults, then runs the service logic.
Task.services.automation.clean_dead_tasks()
```

### When to pick which

| Use‑case                                                          | Call form                                     | Why it makes sense                                                                                                                |
| ----------------------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| Work on **one existing** row                                      | `task.services.mark_done()`                   | You already have the instance; the service mutates it and persists changes.                                                       |
| Run **bulk / maintenance** logic or logic **before** a row exists | `Task.services.automation.clean_dead_tasks()` | You need the behaviour but not a specific row to start from; the service will create its own temporary Task or iterate over many. |

## 6 · Accessing Model Class in Service

- When working inside a service, you may need access to the model class itself to perform database queries.

- The service initialization automatically provides this by setting the model class as an attribute matching the model name.


In the background, our base service sets the target object class as an attribute by the class name. 

Here's how to use it:

```python
# tasks/service/services.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task

class TaskAutomationService(BaseDjangoModelService):    
    task: Task 
    # add for proper type annotations when using database queries
    Task: Task 
    
    def mark_stale(self) -> Task:
        stale_tasks = self.Task.objects.filter(created_date__lte='2020-01-01')
        ...        
```
