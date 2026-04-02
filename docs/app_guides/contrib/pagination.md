# Pagination

> **Purpose:** Provide a simple wrapper around Django's built-in paginator and a pair of template tags that generate pagination URLs and elided page ranges while preserving existing query parameters.

---

## Why Pagination?

List views need consistent pagination across every feature. **The Pagination system** provides:

- A single `paginate_list()` function with sensible defaults for page size
- A `pagination_url` template tag that builds page links without discarding active filters or search terms
- A `get_elided_page_range` template tag for rendering smart page number controls (e.g. `1 2 … 5 6 7 … 19 20`)

---

## Quick Start

### 1. Paginate a Queryset in Your View

```python
from django_spire.contrib.pagination.pagination import paginate_list

def order_list_view(request):
    orders = Order.objects.active().order_by('-created_datetime')

    page = paginate_list(
        object_list=orders,
        page_number=request.GET.get('page', 1),
        per_page=25,
    )

    return render(request, 'orders/page/order_list_page.html', {'page': page})
```

### 2. Render Pagination Controls in Your Template

```html
--8<-- "docs/app_guides/contrib/templates/pagination_controls.html"
```

---

## Core Concepts

### `paginate_list`

Wraps Django's `Paginator` and returns a `Page` object for the requested page number. If the page number exceeds the total number of pages, the last page is returned instead of raising an error.

```python
from django_spire.contrib.pagination.pagination import paginate_list
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `object_list` | `list` or `QuerySet` | required | The items to paginate |
| `page_number` | `int` | `1` | The current page number |
| `per_page` | `int` | `50` | Number of items per page |

Returns a Django `Page` object. All standard `Page` methods apply: `has_next()`, `has_previous()`, `next_page_number()`, `previous_page_number()`, etc.

### `pagination_url` Template Tag

Generates a query string for a pagination link. Preserves all existing GET parameters (search terms, filters, sort order) and updates only the page number.

```html
--8<-- "docs/app_guides/contrib/templates/pagination_load_tags.html"
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page_number` | `int` | required | The target page number |
| `page_name` | `str` | `'page'` | The query parameter name for the page number |

Spaces in existing query parameter values are replaced with `+` to stay consistent with how Django session filters encode values.

### `get_elided_page_range` Template Tag

Returns an elided page range from the paginator — a sequence of page numbers with `'...'` inserted where large gaps exist. Wraps Django's built-in `get_elided_page_range`.

```html
--8<-- "docs/app_guides/contrib/templates/pagination_load_tags.html"
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page_obj` | `Page` | required | The current `Page` object |
| `on_each_side` | `int` | `2` | Number of pages to show on each side of the current page |
| `on_ends` | `int` | `2` | Number of pages to show at each end of the range |

Returns an iterator of integers and `'...'` strings.

---

## Main Operations

### Basic Pagination in a View

```python
from django_spire.contrib.pagination.pagination import paginate_list

def invoice_list_view(request):
    invoices = Invoice.objects.active().order_by('-issued_date')

    page = paginate_list(
        object_list=invoices,
        page_number=request.GET.get('page', 1),
    )

    return render(request, 'invoices/page/invoice_list_page.html', {'page': page})
```

### Preserving Filters Across Page Links

`pagination_url` automatically carries forward all existing GET parameters. No extra configuration is needed — if the current URL is `?search=acme&status=unpaid&page=1`, a link to page 2 becomes `?search=acme&status=unpaid&page=2`.

```html
--8<-- "docs/app_guides/contrib/templates/pagination_next_link.html"
```

### Using a Custom Page Query Parameter

If your view uses a parameter name other than `page` (e.g. when multiple paginated lists appear on the same page):

```html
--8<-- "docs/app_guides/contrib/templates/pagination_custom_param_link.html"
```

Match the same name in your view:

```python
page = paginate_list(
    object_list=invoices,
    page_number=request.GET.get('invoice_page', 1),
)
```

### Rendering an Elided Page Range

For long page ranges, `get_elided_page_range` inserts `'...'` where pages are omitted:

```html
--8<-- "docs/app_guides/contrib/templates/pagination_elided_range.html"
```

To show more pages around the current one:

```html
--8<-- "docs/app_guides/contrib/templates/pagination_elided_custom.html"
```
