# Ordering

> **Purpose:** Provide a flexible system for managing the order of model instances, enabling drag-and-drop reordering, list manipulation, and position-based logic with intelligent validation and efficient bulk updates.

---

## Why Ordering?

Many applications need to manage ordered lists: playlists, task priorities, navigation menus, gallery layouts, etc. **The Ordering system** eliminates manual position management by providing:

- An `order` field automatically added via `OrderingModelMixin`
- A service layer (`OrderingService`) for safe position manipulation
- Validation to prevent invalid positions
- Efficient bulk updates when reordering large sets
- Support for reordering across different querysets (move items between categories)
- Automatic gap handling when inserting items

---

## Quick Start

### 1. Add OrderingModelMixin to Your Model

```python
from django.db import models
from django_spire.contrib.ordering.mixins import OrderingModelMixin
from django_spire.history.mixins import HistoryModelMixin


class Task(HistoryModelMixin, OrderingModelMixin):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
```

### 2. Run Migrations

The mixin adds an `order` field (PositiveIntegerField with default=0) to your model:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Use the Ordering Service

```python
# Get a task and reorder it
task = Task.objects.get(pk=1)
all_tasks = Task.objects.all()

# Move task to position 3 within all tasks
task.ordering_services.processor.move_to_position(
    destination_objects=all_tasks,
    position=3,
)
```

---

## Core Concepts

### The `order` Field

Each model using `OrderingModelMixin` gets:
```python
order = models.PositiveIntegerField(default=0)
```

This field tracks the relative position of items. Positions start at 0 and increment.

### Ordering Service

Available on any model with the mixin:

```python
task.ordering_services.processor
```

The service provides two main methods:
- `move_to_position()` - Relocate an item to a specific position
- `remove_from_objects()` - Remove an item from an ordered list

---

## Main Operations

### Moving an Item to a Position

The most common operation: reorder a single item within a list.

```python
task = Task.objects.get(pk=1)
all_tasks = Task.objects.all()

# Move task to position 2 (0-indexed)
task.ordering_services.processor.move_to_position(
    destination_objects=all_tasks,
    position=2,
)
```

**What happens:**

1. Task at position 2 shifts to position 3
2. All items at position ≥ 2 increment by 1
3. The moved task gets position 2
4. All updates happen in a single database operation (efficient!)

### Moving Between Different Lists

You can move items between different querysets (e.g., move a task from one category to another):

```python
task = Task.objects.get(pk=1)
category_a_tasks = Task.objects.filter(category='A')
category_b_tasks = Task.objects.filter(category='B')

# Move task from category A to position 1 in category B
task.ordering_services.processor.move_to_position(
    destination_objects=category_b_tasks,
    position=1,
    origin_objects=category_a_tasks,
)
```

When `origin_objects` is provided:
1. Items in the origin list get renumbered after the item is removed
2. Items in the destination list at position ≥ 1 get shifted
3. The task gets assigned to the destination position

### Removing an Item from Ordering

Reset an item's order position (useful when soft-deleting or archiving):

```python
task = Task.objects.get(pk=1)
all_tasks = Task.objects.all()

# Remove task from ordering - other items shift down
task.ordering_services.processor.remove_from_objects(
    destination_objects=all_tasks,
)
```

All items after the removed position get renumbered consecutively.

---

## Practical Examples

### Drag-and-Drop Reordering API

A typical drag-and-drop interface sends new positions via JSON. Here's a view handling that:

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django_spire.core.shortcuts import get_object_or_null_obj
from myapp.models import Task


@require_POST
def reorder_task(request, pk, order):
    """Reorder a task to a specific position."""
    task = get_object_or_null_obj(Task, pk=pk)

    if task.id is None:
        return JsonResponse({
            'type': 'error',
            'message': 'Task not found'
        })

    all_tasks = Task.objects.active().order_by('order')

    task.ordering_services.processor.move_to_position(
        destination_objects=all_tasks,
        position=order,
    )
    return JsonResponse({
        'type': 'success',
        'message': 'Task reordered successfully',
    })
```

### Multi-Category Ordering

Managing ordered items across multiple categories (like moving playlists between collections):

```python
def move_track_to_playlist(track_id, new_playlist_id, position):
    track = Track.objects.get(pk=track_id)
    old_playlist_tracks = track.playlist.tracks.all()
    new_playlist = Playlist.objects.get(pk=new_playlist_id)
    new_playlist_tracks = new_playlist.tracks.all()

    # Move from one playlist to another
    track.ordering_services.processor.move_to_position(
        destination_objects=new_playlist_tracks,
        position=position,
        origin_objects=old_playlist_tracks,
    )

    track.playlist = new_playlist
    track.save()
```

---

## Validation

The ordering system validates:

| Validation | Error | Why |
|---|---|---|
| Position is non-negative | `Position must be a positive number.` | Positions cannot be negative |
| Position is an integer | `Position must be a positive number.` | Fractional positions don't make sense |
| Position ≤ list size | `Position must be less than the number of destination objects.` | Can't insert past the end of list |

Validation errors raise `OrderingMixinGroupError` with a list of `OrderingMixinError` objects:

```python
from django_spire.contrib.ordering.exceptions import OrderingMixinGroupError

try:
    task.ordering_services.processor.move_to_position(
        destination_objects=Task.objects.all(),
        position=999,  # Invalid!
    )
except OrderingMixinGroupError as e:
    print(e.message)  # 'Ordering validation failed.'
    for error in e.errors:
        print(error)   # OrderingMixinError details
```

---

## Real-World Example: Task Priority System

Here's a complete example from the test project:

```python
# models.py
from django.db import models
from django_spire.history.activity.mixins import ActivityMixin
from django_spire.history.mixins import HistoryModelMixin
from django_spire.contrib.ordering.mixins import OrderingModelMixin


class Duck(ActivityMixin, HistoryModelMixin, OrderingModelMixin):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#ff0000')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Duck'
        verbose_name_plural = 'Ducks'
        db_table = 'apps_ordering'
```

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from myapp.models import Duck


@require_POST
def reorder_duck(request, pk: int, order: int) -> JsonResponse:
    """Reorder a duck to a specific position."""
    duck = Duck.objects.filter(pk=pk).first()

    if not duck:
        return JsonResponse({
            'type': 'error',
            'message': 'Duck not found'
        }, status=404)

    all_ducks = Duck.objects.active().order_by('order')

    duck.ordering_services.processor.move_to_position(
        destination_objects=all_ducks,
        position=order,
    )
    return JsonResponse({
        'type': 'success',
        'message': 'Duck reordered successfully',
    })
```

---

## API Reference

### OrderingModelMixin

```python
class OrderingModelMixin(models.Model):
    order: PositiveIntegerField
    ordering_services: OrderingService
```

### OrderingService

```python
task.ordering_services.processor.move_to_position(
    destination_objects: QuerySet,
    position: int,
    origin_objects: QuerySet = None,
) -> None
```

Moves the object to a specific position in the destination list. If `origin_objects` is None, uses `destination_objects` for origin.

```python
task.ordering_services.processor.remove_from_objects(
    destination_objects: QuerySet,
) -> None
```

Removes the object from the ordered list, renumbering remaining items.

### Exceptions

```python
class OrderingMixinGroupError(Exception):
    message: str
    errors: List[OrderingMixinError]


class OrderingMixinError(Exception):
    # Individual validation error
```
