# Choices

> **Purpose:** how Django Spire models define field choices — using Django's built-in `TextChoices` and `IntegerChoices` with project conventions for short values, readable labels, and per-app organization.

---

## Why Choices?

Status fields, priorities, and permission levels need a closed set of valid values. Spire uses Django's `TextChoices` / `IntegerChoices` directly — no custom base class — so models, admin, forms, and queries all get the standard Django behaviour for free.

---

## Conventions

| Convention | Example |
|---|---|
| Short values (typically 3 characters) | `NEW = 'new', 'New'` |
| Readable, title-cased labels | `IN_PROGRESS = 'inp', 'In Progress'` |
| One `choices.py` per app | `django_spire/help_desk/choices.py` |
| `CharField(max_length=3, choices=...)` for text choices | see below |
| `IntegerChoices` ordered least → most restrictive for permission levels | `ApiPermissionChoices` |

---

## Defining Choices

### TextChoices

```python
# task/choices.py
from django.db import models


class TaskStatusChoices(models.TextChoices):
    NEW = 'new', 'New'
    IN_PROGRESS = 'inp', 'In Progress'
    DONE = 'com', 'Complete'
    CANCELLED = 'can', 'Cancelled'
```

### IntegerChoices

Use for permission levels or any numeric hierarchy:

```python
# django_spire/api/choices.py
from django.db import models


class ApiPermissionChoices(models.IntegerChoices):
    """Choices for API access levels are required to be in order of least to most restrictive."""

    VIEW = 1, 'View'
    ADD = 2, 'Add'
    CHANGE = 3, 'Change'
    DELETE = 4, 'Delete'
```

---

## Using Choices in Models

```python
from django.db import models
from task.choices import TaskStatusChoices


class Task(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=3,
        choices=TaskStatusChoices.choices,
        default=TaskStatusChoices.NEW,
    )
```

Everything Django gives you for choice fields comes along:

| Feature | Example |
|---|---|
| Named constants | `TaskStatusChoices.NEW` |
| `.choices` | `TaskStatusChoices.choices` |
| `.names` | `TaskStatusChoices.names` |
| `.values` | `TaskStatusChoices.values` |
| `.labels` | `TaskStatusChoices.labels` |
| Human-readable on instances | `task.get_status_display()` |
| Queryset filtering | `Task.objects.filter(status=TaskStatusChoices.DONE)` |

---

## Frontend Integration

You do **not** need a custom JSON endpoint to expose choices to the client. When a model form with a choices field is bound through [django-glue](https://django-glue.stratusadv.com/) (`Glue.form` / `Glue.model`), the client-side glue field receives the choices automatically, so select dropdowns and filters populate without extra wiring.

For seeding, the seeding helpers understand choice enums directly:

```python
'status': Seeder.model.random_field_choice(TaskStatusChoices),
'status': Seeder.model.ordered_field_choice(TaskStatusChoices),
```
