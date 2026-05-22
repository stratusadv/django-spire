# REST Schemas

> **Purpose:** Define Pydantic-based data models that map to REST API responses, providing type-safe field access and a Django-like `.objects` manager interface.

---

## Why REST Schemas?

External API responses need consistent parsing and validation. **The REST Schema system** provides:

- Pydantic `BaseModel` integration for automatic validation
- Type-safe field definitions matching API response structure
- Django model-like `.objects` manager access pattern
- Optional bridge to Django models via `DjangoModelRestSchema`
- Full Pydantic feature support (validators, computed fields, etc.)

---

## Quick Start

### 1. Create a SchemaSet First

The Schema requires a SchemaSet, so create that first (see [SchemaSets](schemaset.md)):

```python title='your_app/rest/schemaset.py'
from django_spire.contrib.rest import RestSchemaSet


class PirateRestSchemaSet(RestSchemaSet['PirateRestSchema']):
    # ... implementation (see SchemaSets documentation)
    pass
```

### 2. Define the Schema

```python title='your_app/rest/schema.py'
from django_spire.contrib.rest import RestSchema

from your_app.rest.schemaset import PirateRestSchemaSet


class PirateRestSchema(RestSchema):
    id: int
    firstName: str
    lastName: str
    email: str
    username: str

    objects = PirateRestSchemaSet.as_manager()
```

### 3. Query Using the Schema

```python
from your_app.rest.schema import PirateRestSchema

# Access data through the .objects manager
pirates = PirateRestSchema.objects.all()
first_pirate = PirateRestSchema.objects.first()
```

---

## Core Concepts

### RestSchema

Abstract base class combining Pydantic's `BaseModel` with a Django-like `.objects` manager.

```python
from django_spire.contrib.rest import RestSchema
```

| Class Attribute | Type | Description |
|-----------------|------|-------------|
| `objects` | `RestSchemaSet` | Manager instance for QuerySet-like operations |

Subclasses must:

1. Define Pydantic field annotations matching the API response
2. Assign a SchemaSet instance to `objects` using `.as_manager()`

### DjangoModelRestSchema

Optional bridge class for schemas that correspond to Django models.

```python
from django_spire.contrib.rest import DjangoModelRestSchema
```

| Abstract Method | Description |
|-----------------|-------------|
| `from_django_model(cls, model)` | Create schema instance from a Django model instance |
| `to_django_model(self)` | Convert schema instance to a Django model instance |

---

## Main Operations

### Defining Schema Fields

Schema fields use standard Pydantic type annotations:

```python title='your_app/rest/schema.py'
from typing import Optional
from datetime import datetime

from django_spire.contrib.rest import RestSchema

from your_app.rest.schemaset import OrderRestSchemaSet


class OrderRestSchema(RestSchema):
    id: int
    order_number: str
    total: float
    status: str
    created_at: datetime
    notes: Optional[str] = None

    objects = OrderRestSchemaSet.as_manager()
```

### Using the Objects Manager

The `.objects` attribute provides a SchemaSet bound to this schema class:

```python
from your_app.rest.schema import PirateRestSchema

# All pirates
all_pirates = PirateRestSchema.objects.all()

# Filtered pirates
filtered = PirateRestSchema.objects.filter(firstName='Jack')

# Chained operations
result = (
    PirateRestSchema.objects
    .filter(lambda p: p.id > 5)
    .order_by('lastName')
    .limit(10)
)
```

### Nested Schemas

For APIs returning nested objects, define nested Pydantic models:

```python title='your_app/rest/schema.py'
from pydantic import BaseModel

from django_spire.contrib.rest import RestSchema

from your_app.rest.schemaset import ShipRestSchemaSet


class CaptainInfo(BaseModel):
    name: str
    rank: str


class ShipRestSchema(RestSchema):
    id: int
    name: str
    captain: CaptainInfo

    objects = ShipRestSchemaSet.as_manager()
```

Access nested fields with dot notation:

```python
ship = ShipRestSchema.objects.first()
print(ship.captain.name)  # "Jack Sparrow"
```

Filter using double-underscore syntax:

```python
ships = ShipRestSchema.objects.filter(captain__name='Jack Sparrow')
```

### Bridging to Django Models

Use `DjangoModelRestSchema` when you need to sync API data with local Django models:

```python title='your_app/rest/schema.py'
from typing import Self

from django_spire.contrib.rest import DjangoModelRestSchema

from your_app.models import Pirate
from your_app.rest.schemaset import PirateRestSchemaSet


class PirateRestSchema(DjangoModelRestSchema):
    id: int
    firstName: str
    lastName: str
    email: str
    username: str

    objects = PirateRestSchemaSet.as_manager()

    @classmethod
    def from_django_model(cls, model: Pirate) -> Self:
        return cls(
            id=model.pk,
            firstName=model.first_name,
            lastName=model.last_name,
            email=model.email,
            username=model.username,
        )

    def to_django_model(self) -> Pirate:
        return Pirate(
            first_name=self.firstName,
            last_name=self.lastName,
            email=self.email,
            username=self.username,
        )
```

### Using Pydantic Features

Since `RestSchema` extends Pydantic's `BaseModel`, you can use all Pydantic features:

```python title='your_app/rest/schema.py'
from pydantic import field_validator, computed_field

from django_spire.contrib.rest import RestSchema

from your_app.rest.schemaset import PirateRestSchemaSet


class PirateRestSchema(RestSchema):
    id: int
    firstName: str
    lastName: str
    email: str

    objects = PirateRestSchemaSet.as_manager()

    @computed_field
    @property
    def full_name(self) -> str:
        return f'{self.firstName} {self.lastName}'

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
```

---

## Common Patterns

### Schema with Optional Fields

```python title='your_app/rest/schema.py'
from typing import Optional

from django_spire.contrib.rest import RestSchema

from your_app.rest.schemaset import CrewMemberRestSchemaSet


class CrewMemberRestSchema(RestSchema):
    id: int
    name: str
    rank: Optional[str] = None
    years_of_service: Optional[int] = None

    objects = CrewMemberRestSchemaSet.as_manager()
```

### Schema with List Fields

```python title='your_app/rest/schema.py'
from django_spire.contrib.rest import RestSchema

from your_app.rest.schemaset import ShipRestSchemaSet


class ShipRestSchema(RestSchema):
    id: int
    name: str
    crew_ids: list[int]
    cargo_manifest: list[str]

    objects = ShipRestSchemaSet.as_manager()
```
