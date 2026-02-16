---
name: service-layer
description: Service layer best practices on django models 
---

# Service Layer Best Practices

## Purpose

The service layer provides each domain model with a predictable "service layer" so that business rules live next to the data and can be invoked as naturally as `Task.objects`.

## 1. Why a Service Layer?

Django's flexibility often scatters business logic across views, utils, managers, and helpers. A dedicated service layer centralizes business rules by pinning them to the model that owns them. Each model exposes a services descriptor that:

- Groups validation, persistence, and side-effects in one place
- Provides easy access from model: `task.services.notification.send_created()`
- Keeps code modular for easy testing
- Avoids circular-import headaches through proper use of future annotations and TYPE_CHECKING guards

### Example:

The example below demonstrates using a simple Task model to showcase service layer functionality:

## 2. What the BaseService Provides

### BaseDjangoModelService Methods

| Method | Purpose |
|--------|---------|
| `validate_model_obj()` | Runs full_clean() on the target object and raises if validation fails. |
| `save_model_obj()` | Calls validate_model_obj() and then save(). This is the primary pipeline used for saving objects. Avoid calling form.save() or object.save() directly; pass everything through save_model_obj() to maintain a controlled pipeline for model persistence. |

**Service Pipeline Pattern:**

By channeling all persistence through `save_model_obj()`, developers ensure that:
- All Request Noise (versioning, metadata, etc.) is routed only through this control path.
- Any advanced state (eg. decoration, pagination, sort conditions) is processed in a single place.

## 3. Building a Service

### 3.1 Files & Directory Structure

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

if TYPE_CHECKING:
    from app.tasks.services.service import TaskService

class Task(models.Model):
    title = models.CharField(max_length=200)
    is_done = models.BooleanField(default=False)
    
    services = TaskService()
    
    def __str__(self) -> str:
        return self.title
```

### 3.3 The Service

```python
# tasks/services/service.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task
    from app.tasks.services.notification_service import TaskNotificationService
    from app.tasks.services.processor_service import TaskProcessorService

class TaskService(BaseDjangoModelService['Task']):
    # target model — must be declared first
    obj: Task    

    # followed by all sub-services that are related to the model
    notification = TaskNotificationService()
    processor = TaskProcessorService()
```

## 4. Common Service Files: Judgement-Based Approach

The table below outlines the typical file structure and responsibilities within the service layer:

| File Path | Class | Responsibility |
|-----------|-------|----------------|
| services/service.py | TaskService | Parent service that composes sub-services and exposes high-level operations |
| services/notification_service.py | TaskNotificationService | Notifications, messaging, and side-effect integrations (e.g., emails, webhooks) |
| services/processor_service.py | TaskProcessorService | Core task processing logic and workflows |
| services/transformation_service.py (optional) | TaskTransformationService | Data transforms or enrichment supporting other services |

Each service should define the target object type (e.g., `obj: Task`) for instance-level operations and may also provide class-level utilities for bulk or maintenance tasks. Keep responsibilities focused and cohesive.

## 5. Class- vs Instance-Level Access

```python
from app.tasks.models import Task

# Instance-level usage – operate on one concrete record
task = Task.objects.get(pk=42)
after = task.services.mark_done()

# Class-level usage – when no specific record rows exist, uses "null" task (pk = None)
Task.services.automation.clean_dead_tasks()
```

### When to Use Each Approach:

| Use-Case | Call form | Rationale |
|----------|-----------|-----------|
| Work on one existing row in db | `task.services.mark_done()` | Direct operations on instance, mutate and persist changes. |
| Run bulk/maintenance logic when no row exists yet | `Task.services.automation.clean_dead_tasks()` | Utilizes natural behavior without specific task, service creates temporary task containment for behavior. |

## 6. Accessing Model Class in Service

When embedded within a service layer, access to the model class is available for database queries and manipulations. Service initialization sets the model class as an attribute matching the model name. In the background, our base service sets the target object class as the attribute by the given class name.

### Pattern Usage:

```python
# tasks/services/service.py
from __future__ import annotations
from typing import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task

class TaskAutomationService(BaseDjangoModelService['Task']):    
    obj: Task

    def mark_stale(self) -> Task:
        stale_tasks = self.obj_class.objects.filter(created_date__lte='2020-01-01')
        # ...
```

The service layer inherits from a base class that exposes `obj_class`, giving you access to the model class for queries and bulk operations. Use this for marking, processing, or reversing events at runtime as necessary for asset management and orchestration.

## 7. Handling Complex Services

As services grow, it’s acceptable—and often desirable—to keep small, private helper methods inside the service to support readability and cohesion. When the logic becomes complex or domain-rich, extract that logic into a dedicated class (or small class cluster) placed in a subdirectory of the related app, and let the service compose and orchestrate it.

### 7.1 Private helpers inside a service

Keep simple, service-specific helpers private to the file. Use a leading underscore to signal intent.

```python
# tasks/services/processor_service.py
from __future__ import annotations
from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task

class TaskProcessorService(BaseDjangoModelService['Task']):
    obj: Task

    def mark_done(self) -> Task:
        self._ensure_can_mark_done()
        self.obj.is_done = True
        return self.save_model_obj()

    # private, service-local validation
    def _ensure_can_mark_done(self) -> None:
        if not self.obj.title:
            raise ValueError("Cannot mark done without a title")
```

### 7.2 Automation services orchestrating notifications

When recurring workflows or time-based checks are needed (e.g., scanning for overdue tasks and notifying users), model-scoped automation services are a good fit. They coordinate queries and delegate messaging to a notification service.

Recommended layout:

```
tasks/
├── models.py
└── services/
    ├── service.py                 # TaskService (orchestrator/parent)
    ├── notification_service.py    # TaskNotificationService (emails, webhooks, etc.)
    └── automation_service.py      # TaskAutomationService (overdue scans, scheduled jobs)
```

Implementation sketch (pseudocode):

```python
# tasks/services/automation_service.py
from __future__ import annotations
from typing import TYPE_CHECKING, Iterable
from django.utils import timezone
from django_spire.contrib.service import BaseDjangoModelService

if TYPE_CHECKING:
    from app.tasks.models import Task
    from app.tasks.services.notification_service import TaskNotificationService


class TaskAutomationService(BaseDjangoModelService['Task']):
    obj: Task  # instance when called from an object; null-like when invoked at class-level

    # composed sub-service; defined on TaskService in service.py
    notification: TaskNotificationService

    def send_overdue_notifications(self, *, as_of=None) -> int:
        """Scan for overdue tasks and send notifications. Returns count sent.
        Designed for class-level calls: Task.services.automation.send_overdue_notifications().
        """
        now = as_of or timezone.now()
        # Example criteria; adjust to your schema (due_at/assignee/status, etc.)
        overdue_qs = self.obj_class.objects.filter(is_done=False, due_at__lt=now)

        sent = 0
        for batch in self._batched(overdue_qs.iterator(), size=200):  # avoid loading everything at once
            for t in batch:
                # Delegate the actual message send to the notification service
                self.notification.send_overdue(t)
                sent += 1
        return sent

    # Private batching helper for memory-safe iteration
    def _batched(self, items: Iterable, size: int):
        batch = []
        for item in items:
            batch.append(item)
            if len(batch) == size:
                yield batch
                batch = []
        if batch:
            yield batch
```

### 7.3 Usage from views or jobs (unchanged boundary)

Views and jobs should call the service layer; services orchestrate notifications. For bulk automations, prefer class-level calls (e.g., from a management command or scheduled job):

```python
# management command or scheduled job
from app.tasks.models import Task

def run_overdue_job():
    sent = Task.services.automation.send_overdue_notifications()
    print(f"Sent {sent} overdue notifications")
```

You can still expose instance-level helpers for one-off actions when appropriate:

```python
def mark_and_notify_view(request, pk: int):
    task = Task.objects.get(pk=pk)
    if not task.is_done:
        task.services.processor.mark_done()
        task.services.notification.send_completed(task)
```

### 7.4 Guidelines

- Start with private helpers inside services; introduce an automation service when workflows are time-based, periodic, or span multiple queries.
- Keep orchestration (queries, batching, retries, handoffs) in services; keep pure formatting of messages inside notification service methods.
- Prefer class-level automation methods for scans across many rows; instance-level for single-record workflows.
- Tests: unit-test notification formatting separately; integration-test automation methods to ensure correct query and delegation.

### 7.5 Naming guidance

- Use explicit names: TaskAutomationService.send_overdue_notifications(), TaskNotificationService.send_overdue(task).
- Keep automation under services/ as a peer to notification and processor services.
- Views, jobs, and commands should call the service layer: Task.services.automation.send_overdue_notifications().

### Best Practices Checklist

1. **Use Future Annotations**: Always use `from __future__ import annotations` at the top of service files
2. **TYPE_CHECKING Guards**: Surround imports with `if TYPE_CHECKING:` blocks to avoid circular imports
3. **Service Structure**: Maintain predictable naming patterns for easy discovery
4. **Documentation**: Document interfaces for complex service interactions
5. **Isolation**: Extend a single instance across service stack using gather states utilities when possible
6. **Consistency**: Always ensure restore type stability using service decorator for validation and interaction