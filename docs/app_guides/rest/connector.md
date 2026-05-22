# REST Connectors

> **Purpose:** Provide a configurable HTTP client abstraction for making requests to external REST APIs, with support for authentication, custom headers, and timeout configuration.

---

## Why REST Connectors?

HTTP requests to external APIs require consistent handling of base URLs, authentication, headers, and error handling. **The REST Connector system** provides:

- Automatic URL building from `base_url`, `base_path`, and request path
- Built-in request methods for GET, POST, PUT, PATCH, DELETE
- Pluggable authentication via `requests.auth.AuthBase`
- Bearer token authentication out of the box
- Configurable timeout and base headers
- Automatic HTTP error handling via `raise_for_status()`

---

## Quick Start

### 1. Define a Connector

```python title='your_app/rest/connector.py'
from django_spire.contrib.rest import BaseRestHttpConnector


class DummyJsonAPIRestConnector(BaseRestHttpConnector):
    base_url = 'https://dummyjson.com'
```

### 2. Use the Connector

```python
connector = DummyJsonAPIRestConnector()

# GET request
response = connector.get('users')
users = response.json()

# GET with query parameters
response = connector.get('users', params={'limit': 10, 'skip': 0})

# POST request
response = connector.post('users', json={'name': 'Jack Sparrow'})
```

---

## Core Concepts

### BaseRestHttpConnector

The base class for all REST connectors. Subclasses must define `base_url`.

```python
from django_spire.contrib.rest import BaseRestHttpConnector
```

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str` | Required | The root URL of the API (e.g., `https://api.example.com`) |
| `base_path` | `str` | `''` | Optional path prefix appended to all requests |
| `base_headers` | `dict` | `{}` | Headers included in every request |
| `timeout` | `int` | `30` | Request timeout in seconds |

| Method | Description |
|--------|-------------|
| `request(method, path, headers, auth, **kwargs)` | Make an HTTP request with full control |
| `get(path, **kwargs)` | Shortcut for GET requests |
| `post(path, **kwargs)` | Shortcut for POST requests |
| `put(path, **kwargs)` | Shortcut for PUT requests |
| `patch(path, **kwargs)` | Shortcut for PATCH requests |
| `delete(path, **kwargs)` | Shortcut for DELETE requests |
| `auth` | Property returning the `AuthBase` instance (default: `None`) |

### BearerAuth

Authentication handler for Bearer token authentication.

```python
from django_spire.contrib.rest.connector.auth.bearer import BearerAuth
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `bearer_token` | `str` | The token to include in the Authorization header |

| Class Attribute | Default | Description |
|-----------------|---------|-------------|
| `auth_header_name` | `'Authorization'` | The header name for the token |

---

## Main Operations

### Creating a Basic Connector

```python title='your_app/rest/connector.py'
from django_spire.contrib.rest import BaseRestHttpConnector


class MyAPIConnector(BaseRestHttpConnector):
    base_url = 'https://api.example.com'
    base_path = 'v1'
    base_headers = {'Accept': 'application/json'}
    timeout = 60
```

All requests will use `https://api.example.com/v1/` as the base.

### Adding Bearer Token Authentication

```python title='your_app/rest/connector.py'
from django.conf import settings
from requests.auth import AuthBase

from django_spire.contrib.rest import BaseRestHttpConnector
from django_spire.contrib.rest.connector.auth.bearer import BearerAuth


class AuthenticatedAPIConnector(BaseRestHttpConnector):
    base_url = 'https://api.example.com'

    @property
    def auth(self) -> AuthBase:
        return BearerAuth(settings.API_TOKEN)
```

The `Authorization: Bearer <token>` header is automatically added to all requests.

### Customizing the Auth Header Name

Some APIs use non-standard header names for authentication. Subclass `BearerAuth` to customize:

```python title='your_app/rest/auth.py'
from django_spire.contrib.rest.connector.auth.bearer import BearerAuth


class CustomBearerAuth(BearerAuth):
    auth_header_name = 'X-Auth-Token'
```

This will send `X-Auth-Token: Bearer <token>` instead of the standard `Authorization` header.

### Making Requests Without Authentication

```python
connector = MyAPIConnector()

# Skip authentication for this request
response = connector.get('public/health', auth=False)
```

### Making Requests With Custom Headers

```python
connector = MyAPIConnector()

response = connector.get(
    'users',
    headers={'X-Custom-Header': 'value'},
)
```

Custom headers are merged with `base_headers`.

### Handling API Responses

```python
connector = MyAPIConnector()

response = connector.get('users')

# The connector calls raise_for_status() automatically
# Access JSON data
data = response.json()

# Access status code
status = response.status_code
```

### URL Building

The connector builds URLs by joining `base_url`, `base_path`, and the request path:

```python
class MyConnector(BaseRestHttpConnector):
    base_url = 'https://api.example.com'
    base_path = 'v2/api'


connector = MyConnector()
# connector.get('users') -> GET https://api.example.com/v2/api/users
# connector.get('/items/') -> GET https://api.example.com/v2/api/items
```

Leading and trailing slashes in the path are normalized.

### Adding Custom Convenience Methods

Add domain-specific methods to your connector for cleaner, more readable code:

```python title='your_app/rest/connector.py'
from requests import Response

from django_spire.contrib.rest import BaseRestHttpConnector


class DummyJsonAPIRestConnector(BaseRestHttpConnector):
    base_url = 'https://dummyjson.com'

    def get_users(self, limit: int = 30, skip: int = 0) -> Response:
        return self.get('users', params={'limit': limit, 'skip': skip})

    def get_user(self, user_id: int) -> Response:
        return self.get(f'users/{user_id}')

    def search_users(self, query: str) -> Response:
        return self.get('users/search', params={'q': query})

    def create_user(self, first_name: str, last_name: str, email: str) -> Response:
        return self.post('users/add', json={
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
        })

    def update_user(self, user_id: int, **fields) -> Response:
        return self.patch(f'users/{user_id}', json=fields)

    def delete_user(self, user_id: int) -> Response:
        return self.delete(f'users/{user_id}')
```

Usage:

```python
connector = DummyJsonAPIRestConnector()

# Clean, readable API calls
users_response = connector.get_users(limit=10)
user_response = connector.get_user(user_id=5)
search_response = connector.search_users(query='Jack')

# Create and update
new_user = connector.create_user(
    first_name='Jack',
    last_name='Sparrow',
    email='jack@blackpearl.com',
)
connector.update_user(user_id=5, firstName='Captain Jack')
```

This pattern encapsulates API-specific paths and parameters, making your codebase more maintainable.

---

## Common Patterns

### Connector with Dynamic Base URL

```python title='your_app/rest/connector.py'
from django.conf import settings

from django_spire.contrib.rest import BaseRestHttpConnector


class EnvironmentAwareConnector(BaseRestHttpConnector):
    base_url = settings.EXTERNAL_API_URL
```

### Connector with Multiple Auth Options

```python title='your_app/rest/connector.py'
from django_spire.contrib.rest import BaseRestHttpConnector
from django_spire.contrib.rest.connector.auth.bearer import BearerAuth


class MultiAuthConnector(BaseRestHttpConnector):
    base_url = 'https://api.example.com'

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key

    @property
    def auth(self):
        if self._api_key:
            return BearerAuth(self._api_key)
        return None
```

Usage:

```python
# Authenticated connector
auth_connector = MultiAuthConnector(api_key='secret-token')

# Unauthenticated connector
public_connector = MultiAuthConnector()
```
