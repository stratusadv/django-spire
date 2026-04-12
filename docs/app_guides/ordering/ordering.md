# Ordering

> **Purpose:** Provide a flexible system for managing the order of model instances, enabling position-based logic, drag-and-drop reordering, and list manipulation with validation and efficient bulk updates.

---

## Why Ordering?

Many applications need to manage ordered lists: task priorities, navigation menus, gallery layouts, playlists, and more. **The Ordering system** eliminates manual position management by providing:

- An `order` field automatically added via `OrderingModelMixin`
- A service layer (`OrderingProcessorService`) for safe position manipulation
- Support for reordering within the same list or moving items between different querysets
- Validation to prevent invalid positions
- Efficient bulk updates when reordering large sets

---

## Quick Start

### 1. Add `OrderingModelMixin` to Your Model

```python
from django.db import models
from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.history.mixins import HistoryModelMixin


class Task(HistoryModelMixin, OrderingModelMixin):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
```

### 2. Run Migrations

The mixin adds an `order` field to your model:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Use the Ordering Service

```python
task = Task.objects.get(pk=1)

task.ordering_services.processor.move_to_position(
    destination_objects=Task.objects.all(),
    position=2,
)
```

---

## Core Concepts

### The `order` Field

Each model using `OrderingModelMixin` gets:

```python
order = models.PositiveIntegerField(default=0)
```

This field tracks the relative position of items. Positions start at `0` and increment.

### The `OrderingModelMixin`

Add this mixin to any model that needs ordering. It provides the `order` field and the `ordering_services` accessor.

```python
from django_spire.contrib.ordering.mixins import OrderingModelMixin
```

### The `OrderingService`

Accessed on any model instance via `ordering_services`. It exposes a `processor` that performs the actual position operations.

```python
task.ordering_services.processor  # OrderingProcessorService instance
```

### The `OrderingMixinValidator`

Runs automatically inside `move_to_position` before any database writes. It validates that the requested position is a non-negative integer and does not exceed the length of the destination list. Validation failures raise `OrderingMixinGroupError`. See the [Exceptions](exceptions.md) guide for details.

---

## Main Operations

### Moving an Item to a Position

Reorder a single item within the same list:

```python
task = Task.objects.get(pk=1)
all_tasks = Task.objects.all()

task.ordering_services.processor.move_to_position(
    destination_objects=all_tasks,
    position=2,
)
```

**What happens:**

1. All items at position ≥ 2 shift up by 1
2. The moved task is assigned position 2
3. All position updates happen in a single bulk database operation

### Moving an Item Between Different Lists

Move an item from one queryset to a position in another — for example, reassigning a task between categories:

```python
task = Task.objects.get(pk=1)
category_a_tasks = Task.objects.filter(category='A')
category_b_tasks = Task.objects.filter(category='B')

task.ordering_services.processor.move_to_position(
    destination_objects=category_b_tasks,
    position=1,
    origin_objects=category_a_tasks,
)
```

When `origin_objects` is provided:

1. Items in the origin list are renumbered after the item is removed
2. Items in the destination list at position ≥ 1 shift up
3. The item is assigned to the destination position

### Removing an Item from Ordering

Reset an item's position and renumber the remaining items — useful when archiving or soft-deleting:

```python
task = Task.objects.get(pk=1)
all_tasks = Task.objects.all()

task.ordering_services.processor.remove_from_objects(
    destination_objects=all_tasks,
)
```

All items after the removed position are renumbered consecutively.

---

## Main Operations in Practice

### Drag-and-Drop Reordering API

A typical drag-and-drop interface sends new positions via JSON. Here's a view handling that:

```python
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django_spire.core.shortcuts import get_object_or_null_obj
from myapp.models import Task


@require_POST
def reorder_task(request, pk, order):
    task = get_object_or_null_obj(Task, pk=pk)

    if task.id is None:
        return JsonResponse({'type': 'error', 'message': 'Task not found'})

    task.ordering_services.processor.move_to_position(
        destination_objects=Task.objects.active().order_by('order'),
        position=order,
    )

    return JsonResponse({'type': 'success', 'message': 'Task reordered successfully'})
```

### Multi-List Ordering

Moving items across multiple ordered groups (e.g. tracks between playlists):

```python
def move_track_to_playlist(track_id, new_playlist_id, position):
    track = Track.objects.get(pk=track_id)
    new_playlist = Playlist.objects.get(pk=new_playlist_id)

    track.ordering_services.processor.move_to_position(
        destination_objects=new_playlist.tracks.all(),
        position=position,
        origin_objects=track.playlist.tracks.all(),
    )

    track.playlist = new_playlist
    track.save()
```
