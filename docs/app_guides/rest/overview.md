# Django Spire REST

> **Purpose:** Provide a Django QuerySet-like interface for consuming external REST APIs, with Pydantic-based schema validation and pluggable HTTP connectors.

---

## Why Django Spire REST?

Consuming external REST APIs often leads to scattered HTTP calls and inconsistent data handling. **The Django Spire REST system** provides:

- Django QuerySet-like syntax for fetching remote data (`.filter()`, `.order_by()`, `.first()`)
- Pydantic-based schema classes for type-safe API response handling
- Pluggable HTTP connectors with built-in authentication support
- Lazy evaluation and result caching for performance
- Support for nested field lookups using double-underscore syntax

---

## Quick Start

### 1. Create a Connector

```python title='your_app/rest/connector.py'
# your_app/rest/schemaset.py
from django_spire.contrib.rest import BaseRestHttpConnector


class MyAPIConnector(BaseRestHttpConnector):
    base_url = 'https://api.example.com'
```

### 2. Create a Schema and SchemaSet

```python title='your_app/rest/schemaset.py'
# your_app/rest/schemaset.py
from django_spire.contrib.rest import RestSchemaSet

from your_app.rest.connector import MyAPIConnector


class UserRestSchemaSet(RestSchemaSet['UserRestSchema']):
    connector = MyAPIConnector()

    # Must be implemented - called under the hood to fetch the data using the connector 
    # when the RestSchemaSet instance is evaluated
    def _read_many(self, **request_params) -> list['UserRestSchema']:
        from your_app.rest.schema import UserRestSchema

        response = self.connector.get('users', params=request_params)
        data = response.json()

        return [UserRestSchema(**user) for user in data.get('users', [])]

    # Optional - used for direct single object access from the API and is
    # called if available when using the RestSchemaSet .get() method 
    def _read_one(self, user_id, **request_params) -> list['UserRestSchema']:
        from your_app.rest.schema import UserRestSchema

        response = self.connector.get(f'users/{user_id}', params=request_params)
        return UserRestSchema(**response.json())
```

```python title='your_app/rest/schema.py'
# your_app/rest/schema.py
from django_spire.contrib.rest import RestSchema

from your_app.rest.schemaset import UserRestSchemaSet


class UserRestSchema(RestSchema):
    id: int
    firstName: str
    lastName: str
    email: str
    username: str

    # The RestSchemaSet subclass defined above
    objects = UserRestSchemaSet.as_manager()
```

### 4. Use Like Django QuerySets

```python
from your_app.rest.schema import UserRestSchema

# Get all users
users = UserRestSchema.objects.all()

# Filter and order
active_users = (
    UserRestSchema.objects
    .filter(lambda u: u.id > 10)
    .order_by('-firstName')
    .limit(5)
)

# Get a single user
user = UserRestSchema.objects.first()
```

That's it! You now have a Django-like interface for querying external REST APIs.

---

## Architecture Overview

The REST client consists of three interconnected components:

| Component | Class | Responsibility |
|-----------|-------|----------------|
| Connector | `BaseRestHttpConnector` | HTTP client for making requests to the API |
| SchemaSet | `RestSchemaSet` | QuerySet-like interface for querying and filtering |
| Schema | `RestSchema` | Pydantic model defining the data structure |

### Data Flow

1. Call `UserRestSchema.objects.filter(...)` on the Schema
2. The SchemaSet builds up filter/order/limit state (lazy)
3. On evaluation, SchemaSet calls `_read_many()` using the Connector
4. Connector makes HTTP request and returns response
5. SchemaSet parses response into Schema instances
6. Filters, ordering, and limits are applied client-side
7. Results are cached for subsequent iterations

---

## Next Steps

- [Connectors](connector.md) - HTTP client configuration and authentication
- [Schemas](schema.md) - Defining data structures with Pydantic
- [SchemaSets](schemaset.md) - QuerySet-like API reference
