# Filtering

> **Purpose:** how list pages in Django Spire handle searching, filtering, and sorting — server-side querysets and the client-side Glue scroll list.

!!! warning
    This guide assumes a working knowledge of [Django Glue](https://django-glue.stratusadv.com/). The scroll list below is built on `QuerySetGlue` and does not replace the core Glue primitives.

---

## Server-Side

### 1 · Compose a QuerySet

List-page querysets combine `HistoryQuerySet` (soft-delete/active state) with `SearchQuerySetMixin` (default search):

```python
# app/person/querysets.py
from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.core.querysets import SearchQuerySetMixin
from django_spire.history.querysets import HistoryQuerySet

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from app.person.models import Person


class PersonQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def bulk_filter(self, filter_data: dict) -> QuerySet[Person]:
        queryset = self

        search = filter_data.get('search', '')
        if search:
            queryset = queryset.search(search)

        return queryset
```

On the model, attach it through a manager:

```python
# app/person/models.py
from app.person.querysets import PersonQuerySet

class Person(HistoryModelMixin):
    objects = PersonQuerySet.as_manager()
```

### 2 · Searching

`SearchQuerySetMixin.search(search_value)` provides a sensible default — every word in the query must match at least one `CharField` (case-insensitive). Override `search()` on the queryset when the default is wrong:

```python
class PersonQuerySet(HistoryQuerySet, SearchQuerySetMixin):
    def search(self, search_value: str | None) -> QuerySet:
        if not search_value:
            return self

        search_value = search_value.strip()
        return self.filter(
            Q(first_name__icontains=search_value) | Q(last_name__icontains=search_value)
        )
```

### 3 · Applying the Filter in a View

`bulk_filter()` receives the raw request GET params and is the single entry point for all list-page filtering:

```python
# app/person/views.py
from django.template.response import TemplateResponse
from app.person.models import Person


def person_list_view(request):
    people = Person.objects.active().bulk_filter(filter_data=request.GET.dict())

    context = {'people': people}
    return TemplateResponse(request, context=context, template='person/page/list_page.html')
```

Pagination is plain Django `Paginator` on top of the filtered queryset; column sorting can be exposed through a `sort_by_column(sort_column, sort_direction)` queryset method that maps request params to a safe `order_by`.

---

## Client-Side (Glue Scroll Lists)

For interactive list pages, Spire ships a base scroll template that wires a `QuerySetGlue` queryset to search, sort, and infinite scroll:

`django_spire/glue/scroll/scroll.html`

```html
{% extends 'django_spire/glue/scroll/scroll.html' %}

{% block scroll_queryset_order_by_field %}name{% endblock %}
{% block scroll_queryset_unique_name %}{{ person_queryset_name }}{% endblock %}
{% block scroll_queryset_filter_field %}description{% endblock %}
{% block increment %}25{% endblock %}

{% block scroll_header %}
    <div class="row">
        <div class="col">
            <input class="form-control" placeholder="Search ..." type="search" x-model.debounce="searchQuery">
        </div>
        <div class="col">
            <button class="btn btn-outline-secondary" type="button" @click="toggleOrder()">
                <i class="bi" :class="orderBy.startsWith('-') ? 'bi-sort-alpha-down-alt' : 'bi-sort-alpha-down'"></i>
            </button>
        </div>
    </div>
{% endblock %}

{% block scroll_item %}
    {# one row of the list #}
{% endblock %}
```

The view binds the queryset with `Glue.queryset`:

```python
Glue.queryset(
    request,
    'people',
    Person.objects.active(),
    Glue.Access.CHANGE,
    fields=['id', 'first_name', 'last_name', 'description'],
)
```

Available on the Alpine component:

| State / Method | Purpose |
| --- | --- |
| `searchQuery` | bound to the search input; debounced, resets and reloads the list |
| `filterField` | the field name the search input filters on |
| `orderBy` | current sort field; prefix with `-` for descending (`toggleOrder()` flips it) |
| `items` | the loaded rows |
| `hasMore` / `loadMoreItems()` | infinite-scroll state; loads `increment` more rows |
| `updateItem(pk, removed)` | refresh or remove one row after a mutation |

Search and sort are applied client-side against the glued data:

```javascript
this.scrollQuerySet = this.scrollQuerySet
    .filter({ [this.filterField + '__icontains']: this.searchQuery })
    .orderBy(this.orderBy)
    .slice(start, stop)
```
