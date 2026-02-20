# JSON Responses

> **Purpose:** Provide typed convenience wrappers around Django's `JsonResponse` so every view returns a consistent `{ type, message, ...extras }` shape that the frontend can handle uniformly.

---

## Why JSON Responses?

Django's built-in `JsonResponse` is unopinionated about structure. Without a convention, different views end up returning `{ "status": "ok" }`, `{ "result": "error" }`, `{ "success": true }`, and so on — making client-side handling messy.

The helpers in `django_spire.contrib.responses.json_response` standardise the envelope:

```json
{
    "type": "success",
    "message": "Treasure saved successfully.",
    "extra_key": "extra_value"
}
```

`type` is always present. `message` is included when provided. Any extra keyword arguments are merged into the response body.

---

## Available Functions

| Function | `type` value |
|---|---|
| `success_json_response(message, **kwargs)` | `"success"` |
| `error_json_response(message, **kwargs)` | `"error"` |
| `info_json_response(message, **kwargs)` | `"info"` |
| `warning_json_response(message, **kwargs)` | `"warning"` |
| `json_response(type, message, **kwargs)` | any valid `ResponseTypeChoices` |

---

## Basic Usage

```python
from django_spire.contrib.responses.json_response import (
    success_json_response,
    error_json_response,
)
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.core.decorators import valid_ajax_request_required
from app.treasure.models import Treasure


@valid_ajax_request_required
def claim_treasure_view(request, pk: int):
    treasure = get_object_or_null_obj(Treasure, pk=pk)

    if treasure.id is None:
        return error_json_response('Treasure not found.')

    treasure.is_claimed = True
    treasure.services.save_model_obj()

    return success_json_response(f'{treasure.name} has been claimed!')
```

The success response body:

```json
{ "type": "success", "message": "Golden Chalice has been claimed!" }
```

The error response body:

```json
{ "type": "error", "message": "Treasure not found." }
```

---

## Passing Extra Data

Any keyword arguments beyond `message` are merged into the response body. This is useful for returning updated data alongside the status.

```python
from django_spire.contrib.responses.json_response import success_json_response
from app.treasure.models import Treasure


@valid_ajax_request_required
def restock_inventory_view(request):
    treasures = list(Treasure.objects.active().values('id', 'name', 'quantity'))

    return success_json_response(
        'Inventory restocked.',
        treasures=treasures,
        total=len(treasures),
    )
```

Response body:

```json
{
    "type": "success",
    "message": "Inventory restocked.",
    "treasures": [...],
    "total": 12
}
```

On the frontend, the extra keys are available directly on the response object passed to `successHandler`:

```javascript
await GlueFetchHelper.tryGlueFetch(url, {
    successHandler: (response) => {
        this.treasures = response.treasures;
        this.total = response.total;
    },
});
```

---

## Using the Base `json_response`

For cases that don't fit neatly into success/error/info/warning, call `json_response` directly with a `ResponseTypeChoices` value or a valid string:

```python
from django_spire.contrib.responses.json_response import json_response
from django_spire.contrib.responses.enums import ResponseTypeChoices


def map_status_view(request):
    return json_response(
        type=ResponseTypeChoices.WARNING,
        message='Storm detected near treasure island. Proceed with caution.',
    )
```

Passing an unrecognised string raises a `ValueError` at the call site, catching mistakes early.

---

## API Reference

```python
from django_spire.contrib.responses.json_response import (
    success_json_response,
    error_json_response,
    info_json_response,
    warning_json_response,
    json_response,
)
```

```python
def success_json_response(message: str | None = None, **kwargs) -> JsonResponse: ...
def error_json_response(message: str | None = None, **kwargs) -> JsonResponse: ...
def info_json_response(message: str | None = None, **kwargs) -> JsonResponse: ...
def warning_json_response(message: str | None = None, **kwargs) -> JsonResponse: ...
def json_response(type: ResponseTypeChoices | str, message: str | None = None, **kwargs) -> JsonResponse: ...
```

### ResponseTypeChoices

```python
from django_spire.contrib.responses.enums import ResponseTypeChoices

ResponseTypeChoices.SUCCESS  # "success"
ResponseTypeChoices.ERROR    # "error"
ResponseTypeChoices.INFO     # "info"
ResponseTypeChoices.WARNING  # "warning"
```
 