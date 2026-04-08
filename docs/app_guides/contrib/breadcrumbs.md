# Breadcrumbs

> **Purpose:** Provide a composable breadcrumb system that builds navigation trails from model objects, form states, and manual entries — keeping breadcrumb logic close to the models that own it.

---

## Why Breadcrumbs?

Navigation context matters for deep page hierarchies. **The Breadcrumbs system** provides:

- A simple `Breadcrumbs` class that acts as an ordered collection of items
- Model-driven breadcrumbs via `base_breadcrumb()` and `breadcrumbs()` methods on your models
- Automatic create/edit labelling for form views
- Composable trails by combining multiple `Breadcrumbs` instances

---

## Quick Start

### 1. Add `breadcrumbs()` to Your Model

```python
from django.urls import reverse
from django_spire.contrib.breadcrumb import Breadcrumbs


class Project(models.Model):
    name = models.CharField(max_length=255)

    @staticmethod
    def base_breadcrumb() -> Breadcrumbs:
        breadcrumbs = Breadcrumbs()
        breadcrumbs.add_breadcrumb(name='Projects', href=reverse('projects:page:list'))
        return breadcrumbs

    def breadcrumbs(self) -> Breadcrumbs:
        breadcrumbs = self.base_breadcrumb()
        breadcrumbs.add_breadcrumb(name=self.name, href=reverse('projects:page:detail', kwargs={'pk': self.pk}))
        return breadcrumbs
```

### 2. Build Breadcrumbs in a View

```python
from django_spire.contrib.breadcrumb import Breadcrumbs

def project_detail_view(request, pk):
    project = Project.objects.get(pk=pk)

    breadcrumbs = Breadcrumbs()
    breadcrumbs.add_obj_breadcrumbs(project)

    return render(request, 'project/detail.html', {'breadcrumbs': breadcrumbs})
```

---

## Core Concepts

### `BreadcrumbItem`

Represents a single crumb with a display name and an optional link.

```python
from django_spire.contrib.breadcrumb.breadcrumbs import BreadcrumbItem
```

| Attribute | Type | Description |
|---|---|---|
| `name` | `str` | Display text for this breadcrumb |
| `href` | `str \| None` | Link URL — `None` for the current (non-linked) crumb |

### `Breadcrumbs`

An ordered collection of `BreadcrumbItem` objects. Supports iteration, `len()`, and combining two instances with `+`.

```python
from django_spire.contrib.breadcrumb import Breadcrumbs
```

Iterating a `Breadcrumbs` instance yields each item as a `BreadcrumbDict` — a plain `{'name': ..., 'href': ...}` dict — making it straightforward to render in templates.

### Model Integration

The breadcrumb system is model-driven. Models implement two methods:

- **`base_breadcrumb()`** — a static method returning the root trail for the model's section (e.g. a "Projects" list link). Used to give any model's breadcrumbs a consistent starting point.
- **`breadcrumbs()`** — an instance method returning the full trail up to and including the current object.

---

## Main Operations

### Adding a Manual Breadcrumb

```python
breadcrumbs = Breadcrumbs()
breadcrumbs.add_breadcrumb(name='Dashboard', href='/dashboard/')
breadcrumbs.add_breadcrumb(name='Current Page')  # No href — renders as plain text
```

### Building from a Model Object

```python
breadcrumbs = Breadcrumbs()
breadcrumbs.add_obj_breadcrumbs(project)
# Calls project.breadcrumbs() and appends the result
```

### Adding Only the Base Breadcrumb

Useful when you want the section root without the object-level crumb:

```python
breadcrumbs = Breadcrumbs()
breadcrumbs.add_base_breadcrumb(Project)
# Calls Project.base_breadcrumb() if it exists
```

### Form Breadcrumbs

Automatically appends the correct label depending on whether the object is being created or edited:

```python
breadcrumbs = Breadcrumbs()
breadcrumbs.add_form_breadcrumbs(project)
# New object (pk is None):  ... > Project > Create
# Existing object:          ... > Project Name > Edit
```

### Combining Two Breadcrumb Trails

```python
section_crumbs = Breadcrumbs()
section_crumbs.add_breadcrumb(name='Admin', href='/admin/')

page_crumbs = Breadcrumbs()
page_crumbs.add_breadcrumb(name='Users', href='/admin/users/')

combined = section_crumbs + page_crumbs
# Admin > Users
```

### Removing and Reversing

```python
breadcrumbs.remove(0)     # Remove the first item
breadcrumbs.reverse()     # Reverse the entire trail (returns self)
```
