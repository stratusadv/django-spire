# Shortcuts

> **Purpose:** Provide a set of utility functions for common model retrieval and request parsing patterns, removing repetitive boilerplate from views and services.

---

## Why Shortcuts?

Django's built-in `get_object_or_404` covers the most common case, but many situations call for softer failure modes — returning an empty instance instead of raising a 404, returning `None` for optional lookups, or resolving a model dynamically from an app label. **The Shortcuts module** covers these patterns in one place.

---

## Core Concepts

### `get_object_or_null_obj`

Retrieves a model instance matching the given filters. If the object does not exist, returns a **new unsaved instance** of the model rather than raising an exception.

```python
from django_spire.core.shortcuts import get_object_or_null_obj
```

This is particularly useful for views that handle both create and update cases with the same code path — a missing `pk` simply returns an empty model ready to be populated.

### `get_object_or_none`

Retrieves a model instance by primary key. Returns `None` if the object does not exist.

```python
from django_spire.core.shortcuts import get_object_or_none
```

Use this when the absence of an object is expected and should be handled gracefully, rather than treated as an error.

### `process_request_body`

Decodes a JSON request body and returns a field from it by key. Defaults to returning the `data` key.

```python
from django_spire.core.shortcuts import process_request_body
```

### `model_object_from_app_label`

Resolves a model instance dynamically using an app label, model name, and primary key — without importing the model directly. Returns `None` if the content type or object does not exist.

```python
from django_spire.core.shortcuts import model_object_from_app_label
```

---

## Main Operations

### Retrieving an Object or a Blank Instance

```python
from django_spire.core.shortcuts import get_object_or_null_obj
from myapp.models import Invoice

# Returns the Invoice if found, otherwise returns Invoice()
invoice = get_object_or_null_obj(Invoice, pk=pk)

if invoice.id is None:
    # Object was not found — treat as new
    ...
```

You can also pass a queryset instead of a model class:

```python
invoice = get_object_or_null_obj(Invoice.objects.active(), pk=pk)
```

### Retrieving an Object or None

```python
from django_spire.core.shortcuts import get_object_or_none
from myapp.models import Invoice

invoice = get_object_or_none(Invoice, pk=pk)

if invoice is None:
    # Object does not exist
    ...
```

### Parsing a JSON Request Body

```python
from django_spire.core.shortcuts import process_request_body

def my_view(request):
    # Returns request.body parsed as JSON, then extracts the 'data' key
    data = process_request_body(request)

    # Extract a specific key instead
    payload = process_request_body(request, key='payload')
```

Pass `key=None` to return the full parsed JSON body without extracting a specific field.

### Resolving a Model by App Label

```python
from django_spire.core.shortcuts import model_object_from_app_label

obj = model_object_from_app_label(
    app_label='blog',
    model_name='blogpost',
    object_pk=42,
)

if obj is None:
    # Content type not found or object does not exist
    ...
```

This is used internally by the comment and activity systems where models are referenced generically by string rather than direct import.

---

## Function Signatures

```python
get_object_or_null_obj(queryset_or_model: QuerySet[T] | type[T], **kwargs) -> T
```
Returns the matching object or a new empty model instance.

```python
get_object_or_none(model: type[T], pk: int, **kwargs) -> T | None
```
Returns the matching object or `None`.

```python
process_request_body(request: HttpRequest, key: str = 'data') -> Any
```
Decodes the JSON request body and returns the value at `key`. Pass `key=None` for the full body.

```python
model_object_from_app_label(app_label: str, model_name: str, object_pk: int) -> Model | None
```
Resolves a model instance by app label, model name, and primary key.
