# SpireTextChoices

> **Purpose:** Extend Django's TextChoices with a JSON serialization method for easy frontend integration and API responses.

---

## Why SpireTextChoices?

Django's `TextChoices` is perfect for defining field choices, but frontend code often needs choices in JSON format for dropdowns, filters, and form population. **SpireTextChoices** adds a single method that converts your choices to JSON automatically, eliminating serialization boilerplate.

---

## Quick Start

### 1. Define Your Choices

```python
from django_spire.contrib.choices import SpireTextChoices


class TaskStatusChoices(SpireTextChoices):
    NEW = 'new', 'New'
    IN_PROGRESS = 'inp', 'In Progress'
    DONE = 'com', 'Complete'
    CANCELLED = 'can', 'Cancelled'
```

### 2. Use in Models

```python
from django.db import models
from myapp.choices import TaskStatusChoices


class Task(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=3,
        choices=TaskStatusChoices.choices,
        default=TaskStatusChoices.NEW,
    )

    def __str__(self):
        return self.name
```

### 3. Get JSON for Frontend

```python
# Python
json_choices = TaskStatusChoices.to_glue_choices()
# Returns: '[["new", "New"], ["inp", "In Progress"], ["com", "Complete"], ["can", "Cancelled"]]'

# In an API view
from django.http import JsonResponse
from myapp.choices import TaskStatusChoices


def task_choices_api(request):
    return JsonResponse({
        'status_choices': TaskStatusChoices.to_glue_choices(),
    })
```

Frontend receives:
```json
{
  "status_choices": [
    ["new", "New"],
    ["inp", "In Progress"],
    ["com", "Complete"],
    ["can", "Cancelled"]
  ]
}
```

---

## What You Get

`SpireTextChoices` inherits everything from Django's `TextChoices`:

| Feature | Available? | Example |
|---|---|---|
| Named constants | ✓ | `TaskStatusChoices.NEW` |
| `.choices` property | ✓ | `TaskStatusChoices.choices` |
| `.names` property | ✓ | `TaskStatusChoices.names` |
| `.values` property | ✓ | `TaskStatusChoices.values` |
| `.labels` property | ✓ | `TaskStatusChoices.labels` |
| `.to_glue_choices()` method | ✓ | **New! JSON output** |
