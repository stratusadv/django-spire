# Navigation & Breadcrumbs

> **Purpose:** Provide a composable breadcrumb system plus a `Navigation` helper that carries page titles, icons, and home links — keeping navigation logic close to the views that own it.

---

## Why Navigation & Breadcrumbs?

Spire pages share a common chrome: a page title, an icon, a home link, and a breadcrumb trail. **The Navigation system** provides:

- A `Navigation` class that bundles page-level metadata (title, icon, help template, home URL) with a `Breadcrumbs` instance
- A simple `Breadcrumbs` class that acts as an ordered collection of crumbs
- Model-aware helpers that build crumbs from a model's `verbose_name` or instance string
- Composable trails by combining multiple `Breadcrumbs` instances with `+`

---

## Quick Start

### 1. Create a `Navigation` Subclass

```python
# myapp/navigation.py
from django_spire.contrib.navigation.navigation import Navigation


class ProjectNavigation(Navigation):
    def __init__(self) -> None:
        super().__init__()
        self.icon_class = 'bi bi-kanban'
        self.breadcrumbs.add('Projects', view_name='projects:page:list')
```

### 2. Build Breadcrumbs in a View

```python
from django.template.response import TemplateResponse

from myapp.navigation import ProjectNavigation


def project_detail_view(request, pk):
    project = Project.objects.get(pk=pk)

    nav = ProjectNavigation()
    nav.page_title = str(project)
    nav.breadcrumbs.add_model_instance_string(project, view_name='projects:page:detail', view_kwargs={'pk': project.pk})

    return TemplateResponse(request, context=nav.as_context(), template='project/page/detail_page.html')
```

`nav.as_context()` returns a dict keyed `django_spire_navigation` containing `page_title`, `home_href`, `icon_class`, `help_template`, and the breadcrumb items — the base templates pick it up automatically.

---

## Core Concepts

### `Navigation`

Page-level navigation metadata. Import from `django_spire.contrib.navigation.navigation`.

| Attribute | Type | Description |
|---|---|---|
| `page_title` | `str \| None` | The page's heading |
| `icon_class` | `str \| None` | Bootstrap icon class shown next to the title |
| `help_template` | `str \| None` | Optional help template to render |
| `home_url` | `str \| None` | View name of the home link (defaults to `DJANGO_SPIRE_NAVIGATION_HOME_URL`) |
| `breadcrumbs` | `Breadcrumbs` | The breadcrumb trail for this page |

Page title helpers:

| Method | Result |
|---|---|
| `nav.set_page_title_from_model_plural_name(Model)` | `verbose_name_plural` (e.g. `Projects`) |
| `nav.set_page_title_from_model_name(Model)` | `verbose_name` (e.g. `Project`) |
| `nav.set_page_title_to_form_action_from_model_instance(instance)` | `Create Project` / `Edit Project` based on whether the instance has a pk |

### `Breadcrumbs`

An ordered collection of breadcrumb items. Import from `django_spire.contrib.navigation.breadcrumbs`. Supports iteration (yielding `{'name': ..., 'href': ...}` dicts), `len()`, and combining two instances with `+`.

A crumb takes a `name` and either a `view_name` (with optional `view_kwargs`) **or** a raw `href` — not both.

---

## Main Operations

### Adding a Manual Breadcrumb

```python
breadcrumbs.add(name='Dashboard', href='/dashboard/')
breadcrumbs.add(name='Current Page')  # No href — renders as plain text
```

### Model-Aware Helpers

```python
breadcrumbs.add_model_plural_name(Project, view_name='projects:page:list')  # 'Projects'
breadcrumbs.add_model_name(Project, view_name='projects:page:detail', view_kwargs={'pk': project.pk})  # 'Project'
breadcrumbs.add_model_instance_string(project, view_name='projects:page:detail', view_kwargs={'pk': project.pk})  # str(project)
breadcrumbs.add_model_instance_form_action(project)  # 'Create' or 'Edit' depending on pk
```

### Combining Two Breadcrumb Trails

```python
section_crumbs = Breadcrumbs()
section_crumbs.add(name='Admin', href='/admin/')

page_crumbs = Breadcrumbs()
page_crumbs.add(name='Users', href='/admin/users/')

combined = section_crumbs + page_crumbs
# Admin > Users
```

### Removing and Reversing

```python
breadcrumbs.remove(0)     # Remove the first item
breadcrumbs.reverse()     # Reverse the entire trail (returns self)
```
