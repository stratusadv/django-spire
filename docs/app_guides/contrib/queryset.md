# QuerySet Utilities

> **Purpose:** Provide reusable queryset mixins and filter helpers that add session-backed filtering, full-text search across CharField columns, choices conversion, and flexible lookup-map filtering to any Django queryset.

---

## Why QuerySet Utilities?

List views repeatedly solve the same problems: apply filter form data, persist filters across page loads, search across text columns, and populate choice widgets. **The QuerySet Utilities system** provides:

- `SessionFilterQuerySetMixin` — integrates a filter form with Django's session layer so filters persist across requests
- `SearchQuerySetMixin` — splits a search string by word and applies `icontains` across every `CharField` on the model
- `ChoicesQueryMixin` — converts any queryset into a list of `(pk, str)` tuples ready for a select widget
- `filter_by_lookup_map` — maps arbitrary form field names to queryset lookup expressions without writing per-field `if` blocks
- `filter_by_model_fields` — filters a queryset directly from a data dict whose keys match the model's field names

---

## Quick Start

### 1. Add Mixins to a Custom QuerySet

```python
from django.db import models
from django_spire.contrib.queryset.mixins import SearchQuerySetMixin, SessionFilterQuerySetMixin

class ProductQuerySet(SearchQuerySetMixin, SessionFilterQuerySetMixin, models.QuerySet):

    def bulk_filter(self, filter_data: dict):
        return filter_by_lookup_map(
            queryset=self,
            lookup_map={
                'category': 'category__name__icontains',
                'status': 'status',
            },
            data=filter_data,
        )
```

### 2. Use in a View

```python
from django_spire.contrib.queryset.filter_tools import filter_by_lookup_map

def product_list_view(request):
    products = (
        Product.objects
        .process_session_filter(
            request=request,
            session_key='product_filter',
            form_class=ProductFilterForm,
        )
        .search(request.GET.get('search', ''))
        .order_by('name')
    )

    return render(request, 'products/page/product_list_page.html', {'products': products})
```

---

## Core Concepts

### `SessionFilterQuerySetMixin`

Integrates a Django form with session-backed filter persistence. Call `process_session_filter()` on a queryset to apply, persist, or clear the active filters.

```python
from django_spire.contrib.queryset.mixins import SessionFilterQuerySetMixin
```

| Method | Description |
|---|---|
| `process_session_filter(request, session_key, form_class, is_from_body=False)` | Read filter data from `request.GET` (or `request.body` if `is_from_body=True`), validate it, update the session, and call `bulk_filter()` with the stored data. Returns `self` (unfiltered) when the action is `CLEAR` or the session is expired. |
| `bulk_filter(filter_data)` | **Abstract.** Implement in your queryset subclass to apply `filter_data` to `self`. |

The mixin reads an `action` key from the submitted data to determine the operation:

| Action value | Behaviour |
|---|---|
| `Filter` | Save form data to the session and apply filters |
| `Clear` | Purge the session and return the unfiltered queryset |

### `SearchQuerySetMixin`

Splits a search string by spaces and ORs `icontains` lookups across every `CharField` on the model for each word.

```python
from django_spire.contrib.queryset.mixins import SearchQuerySetMixin
```

| Method | Description |
|---|---|
| `search(value)` | Filter the queryset to rows where every word in `value` appears in at least one `CharField`. Returns the filtered queryset. |

### `ChoicesQueryMixin`

Converts a queryset into a flat list of `(pk, str)` tuples suitable for a `ChoiceField` or select widget.

```python
from django_spire.contrib.queryset.mixins import ChoicesQueryMixin
```

| Method | Description |
|---|---|
| `to_choices()` | Returns `[(obj.pk, str(obj)), ...]` for every object in the queryset. |

### `filter_by_lookup_map`

Filters a queryset using an explicit mapping from input keys to ORM lookup expressions. Skips any key whose value is `None`, `""`, or `[]`.

```python
from django_spire.contrib.queryset.filter_tools import filter_by_lookup_map
```

| Parameter | Type | Description |
|---|---|---|
| `queryset` | `QuerySet` | The queryset to filter |
| `lookup_map` | `dict` | Maps input data keys to ORM lookup strings (e.g. `{'category': 'category__name__icontains'}`) |
| `data` | `dict` | The filter values, typically from a form's `cleaned_data` or `request.GET` |
| `extra_filters` | `dict` | Additional `filter()` kwargs merged in unconditionally. Defaults to `{}`. |

### `filter_by_model_fields`

Filters a queryset using a data dict whose keys match the model's field names directly. Automatically uses `__in` for sequence values and `_id__in` for `ForeignKey` sequences. Skips `None`, `""`, and `[]`.

```python
from django_spire.contrib.queryset.filter_tools import filter_by_model_fields
```

| Parameter | Type | Description |
|---|---|---|
| `queryset` | `QuerySet` | The queryset to filter |
| `data` | `dict` | Key-value pairs where keys are model field names |

### `SessionFilterActionEnum`

```python
from django_spire.contrib.queryset.enums import SessionFilterActionEnum
```

| Value | Description |
|---|---|
| `FILTER` (`'Filter'`) | Apply the submitted filter data |
| `CLEAR` (`'Clear'`) | Purge the session filter and return unfiltered results |

---

## Main Operations

### Filtering with a Lookup Map

Use `filter_by_lookup_map` when form field names do not directly match ORM lookups, or when you want case-insensitive or related-field lookups:

```python
from django_spire.contrib.queryset.filter_tools import filter_by_lookup_map

def bulk_filter(self, filter_data: dict):
    return filter_by_lookup_map(
        queryset=self,
        lookup_map={
            'status': 'status',
            'assigned_to': 'assigned_to_id',
            'customer_name': 'customer__name__icontains',
        },
        data=filter_data,
    )
```

Only keys present in both `lookup_map` and `data` with non-empty values are applied. The rest are ignored.

### Filtering Directly by Model Fields

Use `filter_by_model_fields` when the data dict keys already match field names on the model:

```python
from django_spire.contrib.queryset.filter_tools import filter_by_model_fields

results = filter_by_model_fields(
    queryset=Order.objects.active(),
    data={
        'status': 'pending',
        'warehouse_id': 3,
    },
)
```

For a list value on a `ForeignKey` field, the lookup becomes `field_id__in` automatically.

### Searching Across Text Fields

```python
products = Product.objects.search(request.GET.get('q', ''))
```

Searching for `'red shirt'` applies two passes: one for `'red'` and one for `'shirt'`, each OR-ed across all `CharField` columns. A row must match both words to be included.

### Converting a QuerySet to Choices

```python
category_choices = Category.objects.active().order_by('name').to_choices()
# [(1, 'Apparel'), (2, 'Footwear'), ...]
```

Pass the result directly to a `ChoiceField` `choices` argument or a select widget.

### Session-Backed Filter in a View

```python
from django_spire.contrib.queryset.mixins import SessionFilterQuerySetMixin

def invoice_list_view(request):
    invoices = (
        Invoice.objects
        .process_session_filter(
            request=request,
            session_key='invoice_filter',
            form_class=InvoiceFilterForm,
        )
        .order_by('-issued_date')
    )

    return render(request, 'invoices/page/invoice_list_page.html', {'invoices': invoices})
```

On the first load the queryset is unfiltered. When the user submits the filter form with `action=Filter`, the form's cleaned data is stored in the session and `bulk_filter()` is called. On subsequent page loads (including pagination), the session data is reapplied without needing the form to be resubmitted. Submitting with `action=Clear` purges the session and returns all records.
