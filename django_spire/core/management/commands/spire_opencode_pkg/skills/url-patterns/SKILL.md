---
name: url-patterns
description: Django URL configuration patterns, namespaces, and nested structure conventions
---

# URL Patterns

## Overview

This skill documents the URL configuration patterns, namespace conventions, and nested URL structure used throughout the Django Spire project. URLs are organized hierarchically to create readable "sentence-like" paths that clearly express their purpose.

### When to Use
- Creating new URL configurations for Django apps
- Understanding existing URL patterns and namespaces
- Adding new URL types (page, form, template, json, file, redirect)
- Reviewing URL structure for consistency

### Key Principles
- **Nested Namespaces**: URLs chain together like sentences (e.g., `company user page list`)
- **Type-Based Segregation**: Separate URLs by type (page/form/template/json/file/redirect)
- **Company Scoping**: All user-facing URLs are scoped under `<uuid:company_slug>/`
- **On-Demand Namespaces**: Only create URL type namespaces when views actually exist

## Core Concepts

### URL Directory Structure

The project uses a hierarchical URL structure:

```
system/urls.py (root)
├── django/admin/
├── django_glue/
├── django_spire/
├── theme/
└── <uuid:company_slug>/ (company-scoped base)
    ├── home/
    ├── catalog/
    ├── company/
    ├── inventory/
    └── user_profile/
```

### URL Type Namespaces

Each app contains only the URL type sub-namespaces it needs:

- **page/** - Read-only page views (list, detail)
- **form/** - Form handling views (create, update, delete)
- **template/** - Template-based views
- **json/** - JSON API endpoints
- **file/** - File upload/download endpoints
- **redirect/** - Redirect handling views

### Creating URL Types On-Demand

**Important:** Only create URL type namespaces when you have actual views to support them.

**DO:**
- Create `page/` namespace only if you have page views (list, detail, etc.)
- Create `form/` namespace only if you have form views (create, update, delete)
- Create `json/` namespace only if you have JSON API endpoints
- Create `file/` namespace only if you have file upload/download views
- Create `template/` namespace only if you have template-based views
- Create `redirect/` namespace only if you have redirect views

**DON'T:**
- Create empty URL type namespaces "just in case"
- Add all URL types to every app regardless of needs
- Create placeholder URL files without corresponding views

**Examples from the codebase:**

- **Home App**: Only has dashboard + `page/` (no form, json, template, file needed)
- **Company App**: Only has `page/`, `form/`, and nested `user/` (no json, template, file needed)
- **User Profile App**: Has `redirect/`, `json/`, `template/` (no page, form, file needed)
- **Catalog App**: Has all types because it needs all of them
- **Inventory App**: Has `page/`, `form/`, `template/` based on its view structure

### Namespace Chaining Pattern

URLs are read as sentences by chaining namespaces:

```
<company_slug>/company/user/page/list/
    ↓         ↓     ↓    ↓     ↓
  company → user → page → list
```

This creates the sentence: "company user page list"

### app_name vs namespace

- **app_name**: Defined in each `urls/__init__.py` - identifies the app
- **namespace**: Defined when including URLs - identifies the URL group
- **Combined URL name**: `{namespace}:{app_name}:{sub_namespace}:{view_name}`

## Implementation Guide

### Step 1: Create URL Directory Structure

```
app/your_app/
├── urls/
│   ├── __init__.py
│   └── {type}_urls.py (only create types you need)
├── views/
│   ├── __init__.py
│   └── {type}_views.py (only create types you need)
```

**Note:** Only create URL type files (`page_urls.py`, `form_urls.py`, etc.) when you have corresponding views. Don't create placeholder files for types you don't need.

### Step 2: Create Main URLs File (urls/__init__.py)

**Only include URL types that you need:**

```python
from __future__ import annotations

from django.urls.conf import include, path


app_name = 'your_app'

# Only include the types you actually have views for
urlpatterns = [
    path('form/', include('app.your_app.urls.form_urls', namespace='form')),
    path('page/', include('app.your_app.urls.page_urls', namespace='page')),
]
```

### Step 3: Create Type-Specific URL Files

#### page_urls.py

```python
from __future__ import annotations

from django.urls import path

from app.your_app.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_view, name='list'),
    path('<int:pk>/detail/', page_views.detail_view, name='detail'),
]
```

#### form_urls.py

```python
from __future__ import annotations

from django.urls import path

from app.your_app.views import form_views


app_name = 'form'

urlpatterns = [
    path('create/', form_views.create_view, name='create'),
    path('<int:pk>/delete/', form_views.delete_view, name='delete'),
    path('<int:pk>/update/', form_views.update_view, name='update'),
    path('create/modal/', form_views.create_modal_view, name='create_modal'),
    path('<int:pk>/delete/modal/', form_views.delete_modal_view, name='delete_modal'),
    path('<int:pk>/update/modal/', form_views.update_modal_view, name='update_modal'),
]
```

#### redirect_urls.py

```python
from __future__ import annotations

from django.urls import path

from app.your_app.views import redirect_views


app_name = 'redirect'

urlpatterns = [
    path('login/', redirect_views.login_redirect_view, name='login'),
    path('callback/', redirect_views.callback_view, name='callback'),
]
```

### Step 4: Register in Root URLs

In `system/urls.py`:

```python
urlpatterns += [
    path('<uuid:company_slug>/', include('app.your_app.urls', namespace='your_app')),
]
```

### Step 5: Reverse URL Names

```python
from django.urls import reverse

# Full URL name with all namespaces
url_name = 'company:your_app:page:list'

# Reverse the URL
url = reverse(url_name, kwargs={'company_slug': company.uuid})
```

### Step 6: Create Nested URL Structures

For deeper nesting (e.g., `catalog/page/entry/`):

```python
# app/catalog/urls/__init__.py
from __future__ import annotations

from django.urls.conf import include, path


app_name = 'catalog'

urlpatterns = [
    path('entry/', include('app.catalog.urls.entry_urls', namespace='entry')),
    path('form/', include('app.catalog.urls.form_urls', namespace='form')),
    path('page/', include('app.catalog.urls.page_urls', namespace='page')),
]
```

```python
# app/catalog/urls/entry_urls.py
from __future__ import annotations

from django.urls.conf import include, path


app_name = 'entry'

urlpatterns = [
    path('page/', include('app.catalog.urls.entry.page_urls', namespace='page')),
    path('form/', include('app.catalog.urls.entry.form_urls', namespace='form')),
]
```

## Examples

### DON'T: Flat URL Structure

```python
# ❌ DON'T: All URLs in one file, hard to navigate
urlpatterns = [
    path('list/', list_view, name='list'),
    path('detail/<int:pk>/', detail_view, name='detail'),
    path('create/', create_view, name='create'),
    path('update/<int:pk>/', update_view, name='update'),
    path('delete/<int:pk>/', delete_view, name='delete'),
]
```

### DO: Nested Type-Based Structure

```python
# ✅ DO: Separated by type, clear organization
# urls/__init__.py
from __future__ import annotations

from django.urls.conf import include, path


urlpatterns = [
    path('form/', include('app.your_app.urls.form_urls', namespace='form')),
    path('page/', include('app.your_app.urls.page_urls', namespace='page')),
]
```

```python
# urls/page_urls.py
from __future__ import annotations

from django.urls import path

from app.your_app.views import page_views


urlpatterns = [
    path('list/', page_views.list_view, name='list'),
    path('<int:pk>/detail/', page_views.detail_view, name='detail'),
]
```

```python
# urls/form_urls.py
from __future__ import annotations

from django.urls import path

from app.your_app.views import form_views


urlpatterns = [
    path('create/', form_views.create_view, name='create'),
    path('<int:pk>/update/', form_views.update_view, name='update'),
]
```

### DON'T: Inconsistent Namespace Usage

```python
# ❌ DON'T: Mixing patterns, unclear hierarchy
urlpatterns = [
    path('list/', include('app.other.urls')),  # No namespace
    path('page/', include('app.other.urls')),  # Inconsistent
]
```

### DO: Consistent Namespace Pattern

```python
# ✅ DO: Clear, consistent hierarchy
from __future__ import annotations

from django.urls.conf import include, path


urlpatterns = [
    path('<uuid:company_slug>/', include('app.your_app.urls', namespace='your_app')),
]
```

```python
# In app/your_app/urls/__init__.py
from __future__ import annotations

from django.urls.conf import include, path


urlpatterns = [
    path('form/', include('app.your_app.urls.form_urls', namespace='form')),
    path('page/', include('app.your_app.urls.page_urls', namespace='page')),
]
```

### Real-World Example: Company User Page List

Full URL path: `<company_slug>/company/user/page/list/`

**URL Chain:**
1. `system/urls.py`: `path('<uuid:company_slug>/', include('app.company.urls', namespace='company'))`
2. `app/company/urls/__init__.py`: `path('user/', include('app.company.user.urls', namespace='user'))`
3. `app/company/user/urls/__init__.py`: `path('page/', include('app.company.user.urls.page_urls', namespace='page'))`
4. `app/company/user/urls/page_urls.py`: `path('list/', page_views.list_page_view, name='list')`

**Reverse URL:**
```python
url = reverse('company:user:page:list', kwargs={'company_slug': company.uuid})
```

## Code Review Checklist

When reviewing URL configuration code, verify the following:

1. **Directory Structure**: URLs are organized in `urls/` subdirectory with type-specific files
2. **app_name Declaration**: Each `urls/__init__.py` defines `app_name`
3. **Namespace Usage**: All `include()` calls specify a `namespace` parameter
4. **Type Segregation**: Page, form, template, json, file, and redirect URLs are separated
5. **Consistent Naming**: URL files follow `{type}_urls.py` naming convention
6. **View Imports**: Views are imported from `views/` directory, not defined in URL files
7. **Path Parameters**: Use appropriate parameter types (`<int:pk>`, `<uuid:slug>`, etc.)
8. **Company Scoping**: User-facing URLs are under `<uuid:company_slug>/` prefix
9. **URL Name Format**: View names use descriptive action names (`list`, `create`, `detail`, `update`, `delete`)
10. **Reverse Compatibility**: URL names can be reversed using full namespace chain
11. **No Duplication**: URL patterns are not duplicated across files
12. **Modal Variants**: Form URLs include both regular and modal versions where appropriate
13. **Future Annotations**: All Python files include `from __future__ import annotations`
14. **Import Consistency**: Use `from django.urls.conf import include, path` consistently
15. **Single Quotes**: All string literals use single quotes per python-style guidelines
16. **TYPE_CHECKING Guards**: Use import guards when circular imports are possible
17. **On-Demand Namespaces**: Only create URL type namespaces when corresponding views exist
