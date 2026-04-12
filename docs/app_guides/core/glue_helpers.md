# Glue Helpers

> **Purpose:** Provide a consistent, retry-aware interface for all client-side Django Glue operations — whether calling a custom JSON endpoint, loading a single model object, or querying a full queryset.

!!! warning
    This guide assumes a working knowledge of [Django Glue](https://django-glue.stratusadv.com/). The helpers wrap the core Django Glue primitives (`django_glue_fetch`, `ModelObjectGlue`, `QuerySetGlue`) and are not a replacement for them.

---

## Why Glue Helpers?

Raw Django Glue calls are powerful but verbose. Every call needs its own error handling, retry logic, and response dispatch. **Glue Helpers** standardise that boilerplate into three focused classes:

| Helper | When to Use |
|---|---|
| `GlueFetchHelper` | Calling a custom JSON endpoint (not a Glue model/queryset) |
| `GlueObjectHelper` | Loading or interacting with a single `ModelObjectGlue` instance |
| `GlueQuerySetHelper` | Querying, filtering, updating, or deleting via a `QuerySetGlue` |

All three extend `GlueRetryHelper`, giving every call built-in retry-on-failure behaviour and automatic error dispatching.

---

## Quick Start

Load a model object on page init and call a custom action endpoint on user interaction.

**Backend:**

```python
from django.http import JsonResponse
from django_spire.contrib.responses.json_response import success_json_response, error_json_response
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.core.decorators import valid_ajax_request_required
from myapp.models import Treasure


@valid_ajax_request_required
def bury_treasure_view(request, pk: int) -> JsonResponse:
    treasure = get_object_or_null_obj(Treasure, pk=pk)

    if treasure.id is None:
        return error_json_response('Treasure not found.')

    treasure.is_buried = True
    treasure.services.save_model_obj()

    return success_json_response(f'{treasure.name} has been buried!')
```

**Frontend:**

```javascript
{
    treasure: new ModelObjectGlue('{ unique_name }'),

    async init() {
        await GlueObjectHelper.tryGlueGet(this.treasure, 3);
    },

    async buryTreasure() {
        const url = `{ url "treasure:bury" pk=0 }`.replace('0', this.treasure.id);

        await GlueFetchHelper.tryGlueFetch(url, {
            successHandler: (response) => {
                console.log(response.message);
            },
        });
    },
}
```

---

## Core Concepts

### `GlueFetchHelper`

Use when calling any custom JSON endpoint — one that does not map directly to a `QuerySetGlue` operation.

```javascript
GlueFetchHelper.tryGlueFetch(url, options)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `url` | `string` | required | The endpoint URL |
| `options.payload` | `Object` | `{}` | Request body data |
| `options.successHandler` | `Function` | — | Called with the response on success |
| `options.errorHandler` | `Function` | — | Called with the response on error |
| `options.method` | `string` | `'POST'` | HTTP method |
| `options.maxRetries` | `number` | `1` | Maximum retry attempts |
| `options.delayMs` | `number` | `100` | Milliseconds between retries |

Returns `{ success: boolean, response?: Object, error?: Error }`.

### `GlueObjectHelper`

Use to load data for a single `ModelObjectGlue` instance — typically during `init()` of an Alpine.js component.

```javascript
GlueObjectHelper.tryGlueGet(glueObject, maxRetries, errorHelper, delayMs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `glueObject` | `ModelObjectGlue` | required | The Glue object to fetch |
| `maxRetries` | `number` | `1` | Maximum retry attempts |
| `errorHelper` | `Function` | `null` | Called after each failed attempt |
| `delayMs` | `number` | `100` | Milliseconds between retries |

### `GlueQuerySetHelper`

Use for any queryset operation — fetching all records, filtering, getting one by id, updating, or deleting.

| Method | Description |
|---|---|
| `tryAll(glueQuerySet, ...)` | Fetch all objects in the queryset |
| `tryFilter(glueQuerySet, filterParams, ...)` | Filter objects by parameters |
| `tryGet(glueQuerySet, id, ...)` | Fetch a single object by id |
| `tryDelete(glueQuerySet, id, ...)` | Delete an object by id |
| `tryUpdate(glueQuerySet, queryModelObject, field, ...)` | Update one or all fields on an object |
| `tryMethod(glueQuerySet, id, method, kwargs, ...)` | Call a named method on an object |
| `tryNullObject(glueQuerySet, ...)` | Fetch the null/empty object from the queryset |
| `tryToChoices(glueQuerySet, filterParams, ...)` | Convert queryset objects to `[value, label]` choice pairs |

All methods share the same optional tail arguments: `maxRetries`, `errorHelper`, `delayMs`.

### Retry Logic

All helpers extend `GlueRetryHelper`, which retries failed calls up to `maxRetries` times with a `delayMs` pause between each attempt. If all retries are exhausted, a generic error event is dispatched automatically — no extra error handling is required in your component.

```javascript
// Retry up to 3 times with a 300ms delay
await GlueQuerySetHelper.tryAll(this.treasure_queryset, 3, null, 300);

// Run a callback between retries
await GlueFetchHelper.tryGlueFetch(url, {
    maxRetries: 3,
    delayMs: 200,
    errorHelper: () => { this.isRetrying = true; },
    successHandler: () => { this.isRetrying = false; },
});
```

---

## Main Operations

### Calling a Custom Endpoint

Call an endpoint and update local state with the response:

```javascript
async discoverLocation(locationId) {
    const url = `{ url "treasure:discover" pk=0 }`.replace('0', locationId);

    await GlueFetchHelper.tryGlueFetch(url, {
        successHandler: (response) => {
            if (response.locations) {
                this.locations = response.locations;
            }
        },
        errorHandler: () => {
            console.error('Could not mark location as discovered.');
        },
        maxRetries: 2,
        delayMs: 200,
    });
}
```

### Loading a Model Object on Init

```javascript
{
    treasure: new ModelObjectGlue('{ unique_name }'),

    async init() {
        await GlueObjectHelper.tryGlueGet(this.treasure, 3);
    },
}
```

### Populating a Select from a QuerySet

```javascript
{
    crew_queryset: new QuerySetGlue('crew_members'),
    assigned_crew: new GlueCharField('assigned_crew'),

    async init() {
        this.assigned_crew.choices = await GlueQuerySetHelper.tryToChoices(this.crew_queryset);
    },
}
```

### Deleting a Record

```javascript
{
    treasures: { treasures|safe },
    treasure_queryset: new QuerySetGlue('treasures'),

    async deleteTreasure(id) {
        await GlueQuerySetHelper.tryDelete(this.treasure_queryset, id, 2);
        this.treasures = this.treasures.filter(t => t.id !== id);
    },
}
```

### Updating a Single Field

```javascript
{
    treasure_queryset: new QuerySetGlue('treasures'),

    async markRecovered(treasureObj) {
        treasureObj.is_recovered = true;
        await GlueQuerySetHelper.tryUpdate(this.treasure_queryset, treasureObj, 'is_recovered');
    },
}
```
