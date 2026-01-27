# SpireModelAdmin

> **Purpose:** Provide a zero-configuration Django admin interface for your models with intelligent defaults that automatically discover fields, filters, search capabilities, and display options.

---

## Why SpireModelAdmin?

Django's admin interface requires manual configuration of `list_display`, `list_filter`, `search_fields`, and more for each model. **SpireModelAdmin** eliminates this boilerplate by analyzing your model's fields and automatically generating sensible defaults:

- Discovers searchable text fields (CharField, TextField)
- Identifies filterable fields (BooleanField, DateField, ForeignKey, choices)
- Generates appropriate list display columns
- Sets readonly fields for audit fields (`created_datetime`, `is_active`, `is_deleted`)
- Enables pagination and ordering out of the box

---

## Quick Start

### 1. Import and Register

```python
# myapp/admin.py
from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from myapp.models import Task


@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task
```

That's it! The admin interface is now fully configured with intelligent defaults.

### 2. Access in Django Admin

Navigate to `/admin/myapp/task/` and you'll see:
- All model fields displayed in the list view (up to 10 columns)
- Search boxes for text-based fields
- Filter sidebar for boolean, date, and foreign key fields
- Readonly display for audit fields
- 25 items per page with newest-first ordering

---

## What Gets Configured Automatically

| Configuration | Auto-behavior | Max items |
|---|---|---|
| **List Display** | All non-relational fields except M2M | 10 columns |
| **Search Fields** | CharField and TextField fields | 5 fields |
| **List Filter** | BooleanField, DateField, ForeignKey, CharField with choices | Unlimited |
| **Readonly Fields** | `created_datetime`, `is_active`, `is_deleted` | Auto-detected |
| **Ordering** | Newest first (`-id`) | Single direction |
| **Pagination** | 25 items per page | Fixed |

---

## Customization

You can override any auto-configured behavior by simply defining it in your admin class:

### Custom List Display

```python
@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task
    list_display = ('id', 'name', 'status', 'assigned_to')
```

When you define `list_display`, SpireModelAdmin respects your choice and doesn't auto-configure.

### Custom Search Fields

```python
@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task
    search_fields = ('name', 'description', 'assigned_to__username')
```

### Custom Filters

```python
@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task
    list_filter = ('status', 'created_datetime', 'assigned_to')
```

### Custom Readonly Fields

```python
@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task
    readonly_fields = ('created_datetime', 'id', 'slug')
```

### Custom Ordering

```python
@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task
    ordering = ('-created_datetime', 'name')
```

### Custom Pagination

```python
@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task
    list_per_page = 50
```

---

## Configuration Limits

You can adjust the limits for auto-discovery to suit your models:

```python
@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task

    # Maximum text fields to include in search
    max_search_fields = 3

    # Maximum columns to display in list view
    max_list_display = 8
```

---

## How It Works

SpireModelAdmin uses Python's `__init_subclass__` hook to automatically configure your admin class when it's defined:

1. **Field Discovery**: Analyzes all model fields using Django's `_meta` API
2. **Smart Exclusions**: Skips M2M fields, reverse relations, and private fields
3. **Categorization**: Groups fields by type (text, boolean, date, foreign key)
4. **Configuration**: Populates list_display, search_fields, list_filter, etc.
5. **Trailing Fields**: Audit fields (`is_active`, `is_deleted`) always appear at the end

The configuration only runs once via `_spire_configured` flag to avoid redundant setup.

---

## Common Patterns

### Model with Foreign Keys

```python
from django.contrib import admin
from django_spire.contrib.admin.admin import SpireModelAdmin
from myapp.models import Task, User


@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task
```

With a model like:
```python
class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=StatusChoices.choices)
    created_datetime = models.DateTimeField(auto_now_add=True)
```

SpireModelAdmin automatically:

- Adds `name` and `description` to search
- Adds `assigned_to` and `status` to filters
- Displays `name`, `description`, `assigned_to`, `status`, `created_datetime`

### Model with Activity Tracking

If your model uses `HistoryModelMixin` or `ActivityMixin`:

```python
@admin.register(Comment)
class CommentAdmin(SpireModelAdmin):
    model_class = Comment
```

The audit fields (`created_datetime`, `is_active`, `is_deleted`) are automatically marked readonly and placed at the end of the list display.

### Combining with Standard Django Admin

You can mix SpireModelAdmin's auto-configuration with traditional Django admin features:

```python
@admin.register(Task)
class TaskAdmin(SpireModelAdmin):
    model_class = Task

    # Auto-configured
    # - list_display, list_filter, search_fields

    # Your custom additions
    actions = ['mark_complete', 'mark_incomplete']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'status')
        }),
        ('Metadata', {
            'fields': ('created_datetime', 'is_active'),
            'classes': ('collapse',)
        }),
    )

    def mark_complete(self, request, queryset):
        queryset.update(status=StatusChoices.COMPLETE)
    mark_complete.short_description = "Mark as complete"
```

!!! note

    Custom `fieldsets` will override the auto-configured layout. Use only the SpireModelAdmin defaults if you want the automatic field discovery.

---

## Field Type Support

SpireModelAdmin recognizes these field types for auto-configuration:

| Field Type | Searchable? | Filterable? | Displayed? |
|---|---|---|---|
| CharField | ✓ | If has choices | ✓ |
| TextField | ✓ | ✗ | ✓ |
| IntegerField | ✗ | ✗ | ✓ |
| BooleanField | ✗ | ✓ | ✓ |
| DateField | ✗ | ✓ | ✓ |
| DateTimeField | ✗ | ✓ | ✓ |
| ForeignKey | ✗ | ✓ | ✓ |
| DecimalField | ✗ | ✗ | ✓ |
| EmailField | ✓ | ✗ | ✓ |

Fields starting with `_` are skipped. ManyToMany and reverse relations are excluded.

---

## Example: Complete Setup

Here's a real-world example from the test project:

```python
# test_project/apps/model_and_service/admin.py
from django.contrib import admin

from django_spire.contrib.admin.admin import SpireModelAdmin
from test_project.apps.model_and_service.models import Adult, Kid


@admin.register(Adult)
class AdultAdmin(SpireModelAdmin):
    model_class = Adult


@admin.register(Kid)
class KidAdmin(SpireModelAdmin):
    model_class = Kid
```

With these models:
```python
class Adult(ActivityMixin, HistoryModelMixin):
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)
    description = models.TextField()
    personality_type = models.CharField(
        max_length=3,
        choices=[('int', 'Introvert'), ('ext', 'Extrovert')],
    )
    email = models.EmailField(blank=True, null=True)
    favorite_number = models.IntegerField()
    birth_date = models.DateField()
    weight_lbs = models.DecimalField(max_digits=7, decimal_places=3)
    best_friend = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'
```

The automatically configured `AdultAdmin` will have:

- **Search**: `first_name`, `last_name`, `description`, `email` (4 out of 5 max)
- **Filters**: `personality_type`, `birth_date`, `best_friend`
- **Display**: `first_name`, `last_name`, `description`, `personality_type`, `email`, `favorite_number`, `birth_date`, `weight_lbs`, `best_friend`, `is_active` (10 columns)
- **Readonly**: `created_datetime`, `is_active`, `is_deleted`
- **Ordering**: Newest first (`-id`)
- **Pagination**: 25 per page
