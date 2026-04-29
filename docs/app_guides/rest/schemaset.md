# REST SchemaSets

> **Purpose:** Provide a Django QuerySet-like interface for querying, filtering, and slicing data from external REST APIs with lazy evaluation and result caching.

---

## Why REST SchemaSets?

Fetching data from REST APIs typically involves imperative HTTP calls and manual result processing. **The REST SchemaSet system** provides:

- Declarative, Django QuerySet-like method chaining (`.filter()`, `.order_by()`, `.limit()`)
- Lazy evaluation - HTTP requests only happen when data is accessed
- Result caching to avoid redundant API calls
- Support for both lambda predicates and Django-style field lookups
- Nested field filtering using double-underscore syntax
- Slicing and indexing support

---

## Quick Start

### 1. Create a Connector

```python title='your_app/rest/connector.py'
from django_spire.contrib.rest import BaseRestHttpConnector


class DummyJsonAPIRestConnector(BaseRestHttpConnector):
    base_url = 'https://dummyjson.com'
```

### 2. Define the SchemaSet

```python title='your_app/rest/schemaset.py'
from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.rest import RestSchemaSet

from your_app.rest.connector import DummyJsonAPIRestConnector

if TYPE_CHECKING:
    from your_app.rest.schema import PirateRestSchema


class PirateRestSchemaSet(RestSchemaSet['PirateRestSchema']):
    connector = DummyJsonAPIRestConnector()

    def _read_many(self, **request_params) -> list[PirateRestSchema]:
        from your_app.rest.schema import PirateRestSchema

        response = self.connector.get('users', params=request_params)
        data = response.json()

        return [PirateRestSchema(**user) for user in data.get('users', [])]
```

### 3. Use QuerySet-Like Methods

```python
from your_app.rest.schema import PirateRestSchema

# All records
pirates = PirateRestSchema.objects.all()

# Filter by field
pirates = PirateRestSchema.objects.filter(firstName='Jack')

# Filter with lambda
pirates = PirateRestSchema.objects.filter(lambda p: p.id > 10)

# Order and limit
pirates = PirateRestSchema.objects.order_by('-lastName').limit(5)

# Get first result
pirate = PirateRestSchema.objects.first()
```

---

## Core Concepts

### RestSchemaSet

Abstract generic class providing a QuerySet-like interface for REST data.

```python
from django_spire.contrib.rest import RestSchemaSet
```

| Class Attribute | Type | Description |
|-----------------|------|-------------|
| `connector` | `BaseRestHttpConnector` | The HTTP connector instance for making requests |

| Abstract Method | Description |
|-----------------|-------------|
| `_read_many(**request_params)` | Fetch and return a list of schema instances |

| Optional Method | Description |
|-----------------|-------------|
| `_read_one(**request_params)` | Fetch a single schema instance (optimization for `.get()`) |

### Lazy Evaluation

SchemaSets are lazy - they do not make HTTP requests until you iterate over them or call a terminal method.

**Terminal methods** (trigger evaluation):

- `list()`, `for` loop, `len()`, `bool()`
- `.first()`, `.last()`, `.get()`, `.count()`, `.exists()`
- `.values_list()`

**Non-terminal methods** (return new SchemaSet):

- `.all()`, `.filter()`, `.exclude()`, `.order_by()`, `.limit()`, `.offset()`
- Slicing with `[:]`

### Result Caching

After evaluation, results are cached within the SchemaSet instance. Subsequent iterations reuse the cached data.

```python
pirates = PirateRestSchema.objects.filter(firstName='Jack')

# First iteration: makes HTTP request
for p in pirates:
    print(p.username)

# Second iteration: uses cached results
for p in pirates:
    print(p.email)
```

Creating a new SchemaSet via chaining clears the cache:

```python
pirates = PirateRestSchema.objects.all()  # HTTP request on iteration
filtered = pirates.filter(id=1)  # New SchemaSet, cache not shared
```

---

## Main Operations

### Filtering with Field Lookups

Filter using keyword arguments that match schema field names:

```python
# Exact match
pirates = PirateRestSchema.objects.filter(firstName='Jack')

# Multiple conditions (AND)
pirates = PirateRestSchema.objects.filter(firstName='Jack', lastName='Sparrow')
```

### Filtering with Lambda Predicates

Filter using custom functions for complex conditions:

```python
# Single condition
pirates = PirateRestSchema.objects.filter(lambda p: p.id > 10)

# Complex condition
pirates = PirateRestSchema.objects.filter(
    lambda p: p.firstName.startswith('J') and p.id < 100
)
```

### Filtering Nested Fields

Use double-underscore syntax for nested field access:

```python
# Schema with nested object
class ShipRestSchema(RestSchema):
    captain: CaptainInfo  # has 'name' field


# Filter by nested field
ships = ShipRestSchema.objects.filter(captain__name='Jack Sparrow')
```

### Excluding Records

Exclude records matching conditions (inverse of filter):

```python
# Exclude by field
pirates = PirateRestSchema.objects.exclude(firstName='Will')

# Exclude with lambda
pirates = PirateRestSchema.objects.exclude(lambda p: p.id < 5)
```

### Ordering Results

Order by one or more fields. Prefix with `-` for descending:

```python
# Ascending
pirates = PirateRestSchema.objects.order_by('firstName')

# Descending
pirates = PirateRestSchema.objects.order_by('-firstName')

# Multiple fields
pirates = PirateRestSchema.objects.order_by('-lastName', 'firstName')
```

### Limiting and Offsetting

Control result count and starting position:

```python
# First 10 results
pirates = PirateRestSchema.objects.limit(10)

# Skip first 5, take next 10
pirates = PirateRestSchema.objects.offset(5).limit(10)

# Using slice syntax
pirates = PirateRestSchema.objects.all()[5:15]
```

### Getting Single Records

Retrieve individual records:

```python
# First result (or None)
pirate = PirateRestSchema.objects.first()

# Last result (or None)
pirate = PirateRestSchema.objects.last()

# Exactly one result (raises LookupError if 0 or >1)
pirate = PirateRestSchema.objects.get(username='jack_sparrow')

# By index
pirate = PirateRestSchema.objects.all()[0]
```

### Counting and Existence Checks

```python
# Count results
count = PirateRestSchema.objects.filter(firstName='Jack').count()

# Check if any exist
has_jacks = PirateRestSchema.objects.filter(firstName='Jack').exists()
```

### Extracting Field Values

Get specific field values as lists:

```python
# Single field (flat list)
usernames = PirateRestSchema.objects.values_list('username', flat=True)
# ['jack_sparrow', 'will_turner', ...]

# Multiple fields (list of tuples)
names = PirateRestSchema.objects.values_list('firstName', 'lastName')
# [('Jack', 'Sparrow'), ('Will', 'Turner'), ...]
```

### Passing Parameters to the API

Use `with_request_params()` to pass query parameters to the underlying HTTP request:

```python
# Pass pagination params to the API
pirates = (
    PirateRestSchema.objects
    .with_request_params(limit=50, skip=100)
    .all()
)
```

These parameters are passed to `_read_many()` as `**request_params`.

### Chaining Operations

All non-terminal methods return new SchemaSet instances and can be chained:

```python
result = (
    PirateRestSchema.objects
    .with_request_params(limit=100)
    .filter(lambda p: p.id > 10)
    .exclude(firstName='Will')
    .order_by('-lastName', 'firstName')
    .limit(20)
    .offset(5)
)

# Evaluate
pirates = list(result)
```

---

## Implementing SchemaSets

### The _read_many Method

The `_read_many` method is abstract and must be implemented. It receives any parameters from `with_request_params()`:

```python title='your_app/rest/schemaset.py'
class PirateRestSchemaSet(RestSchemaSet['PirateRestSchema']):
    connector = DummyJsonAPIRestConnector()

    def _read_many(self, **request_params) -> list[PirateRestSchema]:
        from your_app.rest.schema import PirateRestSchema

        # Make HTTP request with optional params
        response = self.connector.get('users', params=request_params)
        data = response.json()

        # Parse response and return schema instances
        return [PirateRestSchema(**user) for user in data.get('users', [])]
```

### The _read_one Method (Optional)

Override `_read_one` for efficient single-record fetches:

```python title='your_app/rest/schemaset.py'
class PirateRestSchemaSet(RestSchemaSet['PirateRestSchema']):
    connector = DummyJsonAPIRestConnector()

    def _read_many(self, **request_params) -> list[PirateRestSchema]:
        from your_app.rest.schema import PirateRestSchema

        response = self.connector.get('users', params=request_params)
        data = response.json()

        return [PirateRestSchema(**user) for user in data.get('users', [])]

    def _read_one(self, **request_params) -> PirateRestSchema:
        from your_app.rest.schema import PirateRestSchema

        user_id = request_params.get('id')
        response = self.connector.get(f'users/{user_id}')

        return PirateRestSchema(**response.json())
```

---

## API Reference

### Query Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `all()` | `Self` | Returns a clone of the SchemaSet |
| `filter(predicate=None, **kwargs)` | `Self` | Filter by predicate and/or field lookups |
| `exclude(predicate=None, **kwargs)` | `Self` | Exclude matching records |
| `order_by(*fields)` | `Self` | Order by fields (prefix `-` for descending) |
| `limit(n)` | `Self` | Limit to n results |
| `offset(n)` | `Self` | Skip first n results |
| `with_request_params(**kwargs)` | `Self` | Pass parameters to `_read_many()` |

### Terminal Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `first()` | `TSchema \| None` | First result or None |
| `last()` | `TSchema \| None` | Last result or None |
| `get(**kwargs)` | `TSchema` | Exactly one result (raises `LookupError` if 0 or >1) |
| `count()` | `int` | Number of results |
| `exists()` | `bool` | True if any results exist |
| `values_list(*fields, flat=False)` | `list` | Extract field values |

### Dunder Methods

| Method | Description |
|--------|-------------|
| `__iter__` | Iterate over results |
| `__len__` | Get result count |
| `__bool__` | True if results exist |
| `__getitem__` | Index or slice access |
| `__repr__` | String representation |

---

## Common Patterns

### Handling Paginated APIs

When the external API returns paginated data, handle it in `_read_many`:

```python title='your_app/rest/schemaset.py'
class PirateRestSchemaSet(RestSchemaSet['PirateRestSchema']):
    connector = DummyJsonAPIRestConnector()

    def _read_many(self, **request_params) -> list[PirateRestSchema]:
        from your_app.rest.schema import PirateRestSchema

        all_users = []
        skip = request_params.get('skip', 0)
        limit = request_params.get('limit', 100)

        while True:
            response = self.connector.get('users', params={'skip': skip, 'limit': limit})
            data = response.json()
            users = data.get('users', [])

            if not users:
                break

            all_users.extend([PirateRestSchema(**user) for user in users])
            skip += limit

            if len(users) < limit:
                break

        return all_users
```

### Handling Nested API Responses

When the API response is nested:

```python title='your_app/rest/schemaset.py'
class PirateRestSchemaSet(RestSchemaSet['PirateRestSchema']):
    connector = DummyJsonAPIRestConnector()

    def _read_many(self, **request_params) -> list[PirateRestSchema]:
        from your_app.rest.schema import PirateRestSchema

        response = self.connector.get('users', params=request_params)
        data = response.json()

        # Handle nested structure: {"data": {"users": [...]}}
        users = data.get('data', {}).get('users', [])

        return [PirateRestSchema(**user) for user in users]
```

### Using with Django Views

```python title='your_app/views.py'
from django.template.response import TemplateResponse

from your_app.rest.schema import PirateRestSchema


def pirate_list_view(request):
    pirates = PirateRestSchema.objects.order_by('lastName').limit(25)

    return TemplateResponse(
        request=request,
        context={'pirates': pirates},
        template='pirates/list.html',
    )
```
