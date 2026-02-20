# GlueHelpers (JavaScript)

> **Purpose:** Provide a consistent, retry-aware interface for all client-side Django Glue operations — whether calling a custom JSON endpoint, loading a single model object, or querying a full queryset.

!!! warning
    This guide assumes a working knowledge of [Django Glue](https://django-glue.stratusadv.com/). The helpers wrap the core Django Glue primitives (`django_glue_fetch`, `ModelObjectGlue`, `QuerySetGlue`) and are not a replacement for them.

---

## Why GlueHelpers?

Raw Django Glue calls are powerful but verbose. Every call needs its own error handling, retry logic, and response dispatch. **GlueHelpers** standardise that boilerplate into three focused classes:

| Helper | When to Use |
|---|---|
| `GlueFetchHelper` | Calling a custom JSON endpoint (not a Glue model/queryset) |
| `GlueObjectHelper` | Loading or interacting with a single `ModelObjectGlue` instance |
| `GlueQuerySetHelper` | Querying, filtering, updating, or deleting via a `QuerySetGlue` |

All three extend `GlueRetryHelper`, giving every call built-in retry-on-failure behaviour and automatic error dispatching.

---

## Quick Start

The fastest way to see GlueHelpers in action is a page that loads model data on init and lets the user trigger a custom action.

### Backend

```python title='app/treasure/views.py'
from django.http import JsonResponse
from django_spire.contrib.responses.json_response import (
    success_json_response,
    error_json_response
)
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.core.decorators import valid_ajax_request_required
from app.treasure.models import Treasure


@valid_ajax_request_required
def bury_treasure_view(request, pk: int) -> JsonResponse:
    treasure = get_object_or_null_obj(Treasure, pk=pk)

    if treasure.id is None:
        return error_json_response('Treasure not found.')

    treasure.is_buried = True
    treasure.services.save_model_obj()

    return success_json_response(f'{treasure.name} has been buried!')
```

### Frontend

```html title='treasure/page/treasure_page.html'
<div
    x-data="{
        treasure: new ModelObjectGlue('{{ unique_name }}'),

        async init() {
            await GlueObjectHelper.tryGlueGet(this.treasure, 3);
        },

        async buryTreasure() {
            const url = `{% url "treasure:bury" pk=0 %}`.replace('0', this.treasure.id);

            await GlueFetchHelper.tryGlueFetch(url, {
                successHandler: (response) => {
                    console.log(response.message);
                },
            });
        },
    }"
>
    <span x-text="treasure.name"></span>
    <button @click="buryTreasure()">Bury It!</button>
</div>
```

---

## GlueFetchHelper

Use `GlueFetchHelper.tryGlueFetch` when calling any custom JSON endpoint — one that does not map directly to a `QuerySetGlue` operation.

### Method Signature

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
| `options.contentType` | `string` | `'application/json'` | Content-Type header |
| `options.responseType` | `string` | `'json'` | Response type (`json`, `text`, `blob`) |
| `options.headerOptions` | `Object` | `{}` | Additional request headers |
| `options.defaultErrorMessage` | `string` | generic error | Fallback error message |
| `options.maxRetries` | `number` | `1` | Maximum retry attempts |
| `options.errorHelper` | `Function` | `null` | Called after each failed attempt |
| `options.delayMs` | `number` | `100` | Milliseconds between retries |

Returns `{ success: boolean, response?: Object, error?: Error }`.

### Example — Custom Action Endpoint

This example calls a custom endpoint when the user marks a map location as discovered, then updates the local list with the response data.

**Backend:**

```python title='app/treasure/views.py'
from django.http import JsonResponse
from django_spire.contrib.responses.json_response import (
    success_json_response,
    error_json_response
)
from django_spire.core.shortcuts import get_object_or_null_obj
from django_spire.core.decorators import valid_ajax_request_required
from app.treasure.models import TreasureMap


@valid_ajax_request_required
def mark_location_discovered_view(request, pk: int) -> JsonResponse:
    location = get_object_or_null_obj(TreasureMap, pk=pk)

    if location.id is None:
        return error_json_response('Location not found.')

    location.is_discovered = True
    location.services.save_model_obj()

    updated_locations = list(
        TreasureMap.objects.active().values('id', 'name', 'is_discovered').order_by('name')
    )

    return success_json_response(
        message=f'{location.name} marked as discovered!',
        locations=updated_locations
    )
```

**Frontend:**

```html title='treasure/page/map_page.html'
<div
    x-data="{
        locations: {{ locations|safe }},

        async discoverLocation(locationId) {
            const url = `{% url "treasure:discover" pk=0 %}`.replace('0', locationId);

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
        },
    }"
>
    <template x-for="location in locations" :key="location.id">
        <div>
            <span x-text="location.name"></span>
            <button @click="discoverLocation(location.id)" x-show="!location.is_discovered">
                Discover
            </button>
        </div>
    </template>
</div>
```

---

## GlueObjectHelper

Use `GlueObjectHelper.tryGlueGet` to load data for a single `ModelObjectGlue` instance — typically during `init()` of an Alpine.js component.

### Method Signature

```javascript
GlueObjectHelper.tryGlueGet(glueObject, maxRetries, errorHelper, delayMs)
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `glueObject` | `ModelObjectGlue` | required | The Glue object to fetch |
| `maxRetries` | `number` | `1` | Maximum retry attempts |
| `errorHelper` | `Function` | `null` | Called after each failed attempt |
| `delayMs` | `number` | `100` | Milliseconds between retries |

### Example — Editing a Record in a Modal

A modal form loads the treasure's current data before the user can edit it.

**Backend:**

```python title='app/treasure/views.py'
from django.template.response import TemplateResponse
import django_glue as dg

from app.treature.models import Treasure


def treasure_form_modal_view(request, pk: int) -> TemplateResponse:
    treasure = dg.model_object(request, 'treasure', Treasure, pk=pk, fields=['name', 'island', 'value'])

    return TemplateResponse(
        request=request,
        template='treasure/modal/content/treasure_form_modal.html',
        context={'unique_name': treasure.unique_name, 'action_url': request.path},
    )
```

**Frontend:**

```html title='treasure/modal/content/treasure_form_modal.html'
<form
    x-data="{
        treasure: new ModelObjectGlue('{{ unique_name }}'),

        async init() {
            await GlueObjectHelper.tryGlueGet(this.treasure, 3);
        },
    }"
    method="post"
    action="{{ action_url }}"
>
    {% csrf_token %}

    <div class="row g-3 mb-3">
        <div class="col">
            % include 'django_glue/form/field/char_field.html' with glue_model_field='treasure.name' %
        </div>
        <div class="col">
            % include 'django_glue/form/field/char_field.html' with glue_model_field='treasure.island' %
        </div>
        <div class="col">
            % include 'django_glue/form/field/number_field.html' with glue_model_field='treasure.value' %
        </div>
    </div>

    <div class="row g-3">
        <div class="col-12">
            % include 'django_spire/contrib/form/button/form_submit_button.html' %
        </div>
    </div>
</form>
```

---

## GlueQuerySetHelper

Use `GlueQuerySetHelper` for any queryset operation — fetching all records, filtering, getting one by id, updating, or deleting.

### Available Methods

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

### Example — Populating a Filter Form

A filter form loads pirate crew members as choice options when it initialises.

**Backend:**

```python title='app/treasure/views.py'
from django.template.response import TemplateResponse
import django_glue as dg

from app.pirate.crew.models import PirateCrew


def treasure_filter_form_view(request) -> TemplateResponse:
    crew_members = dg.queryset(request, 'crew_members', PirateCrew.objects.active())

    return TemplateResponse(
        request=request,
        template='treasure/form/filter_form.html',
    )
```

**Frontend:**

```html title='treasure/form/filter_form.html'
{% extends 'django_spire/filtering/form/base_session_filter_form.html' %}
{% load session_tags %}

{% block session_filter_key %}{{ filter_session.session_key }}{% endblock %}

{% block filter_content %}
    <div
        class="row g-2"
        x-data="{
            crew_queryset: new QuerySetGlue('crew_members'),
            assigned_crew: new GlueCharField('assigned_crew'),
            search: new GlueCharField(
                'search',
                {
                    value: '{{ filter_session.search|default:&quot;&quot; }}',
                    label: 'Search',
                    name: 'search',
                }
            ),

            async init() {
                this.search.set_attribute('placeholder', 'Search treasure...')
                this.assigned_crew.choices = await GlueQuerySetHelper.tryToChoices(this.crew_queryset);
                this.assigned_crew.value = this.session_controller.get_data('assigned_crew', '');
                this.assigned_crew.required = false;
            },
        }"
    >
        <div class="col-6">
            % include 'django_glue/form/field/char_field.html' with glue_field='search' %
        </div>
        <div class="col-6">
            % include 'django_glue/form/field/multi_select_field.html' with glue_field='assigned_crew' %
        </div>
    </div>
{% endblock %}
```

### Example — Deleting a Record

```html title='treasure/page/treasure_list_page.html'
<div
    x-data="{
        treasures: {{ treasures|safe }},
        treasure_queryset: new QuerySetGlue('treasures'),

        async deleteTreasure(id) {
            await GlueQuerySetHelper.tryDelete(this.treasure_queryset, id, 2);
            this.treasures = this.treasures.filter(t => t.id !== id);
        },
    }"
>
    <template x-for="treasure in treasures" :key="treasure.id">
        <div>
            <span x-text="treasure.name"></span>
            <button @click="deleteTreasure(treasure.id)">Remove</button>
        </div>
    </template>
</div>
```

### Example — Updating a Single Field

```html title='treasure/page/treasure_list_page.html'
<div
    x-data="{
        treasure_queryset: new QuerySetGlue('treasures'),

        async markRecovered(treasureObj) {
            treasureObj.is_recovered = true;

            await GlueQuerySetHelper.tryUpdate(
                this.treasure_queryset,
                treasureObj,
                'is_recovered',
            );
        },
    }"
>
    ...
</div>
```

---

## Retry Logic

All helpers extend `GlueRetryHelper`, which provides automatic retry behaviour.

```javascript
// Retry up to 3 times with a 300ms delay between attempts
await GlueQuerySetHelper.tryAll(this.treasure_queryset, 3, null, 300);

// Run a callback between retries (e.g. show a loading indicator)
await GlueFetchHelper.tryGlueFetch(url, {
    maxRetries: 3,
    delayMs: 200,
    errorHelper: () => { this.isRetrying = true; },
    successHandler: (response) => { this.isRetrying = false; },
});
```

If all retry attempts are exhausted, `GlueRetryHelper` dispatches a generic error event automatically — no extra error handling required in your component.

---

## API Reference

### GlueFetchHelper

```javascript
static async tryGlueFetch(url, {
    payload = {},
    successHandler,
    errorHandler,
    method = 'POST',
    contentType = 'application/json',
    responseType = 'json',
    headerOptions = {},
    defaultErrorMessage,
    maxRetries = 1,
    errorHelper = null,
    delayMs = 100,
} = {})
// Returns: Promise<{ success: boolean, response?: Object, error?: Error }>
```

### GlueObjectHelper

```javascript
static async tryGlueGet(glueObject, maxRetries = 1, errorHelper = null, delayMs = 100)
// Returns: Promise<{ success: boolean }>
```

### GlueQuerySetHelper

```javascript
static async tryAll(glueQuerySet, maxRetries = 1, errorHelper = null, delayMs = 100)
// Returns: Promise<Array>

static async tryFilter(glueQuerySet, filterParams = {}, maxRetries = 1, errorHelper = null, delayMs = 100)
// Returns: Promise<Array>

static async tryGet(glueQuerySet, id, maxRetries = 1, errorHelper = null, delayMs = 100)
// Returns: Promise<ModelObjectGlue>

static async tryDelete(glueQuerySet, id, maxRetries = 1, errorHelper = null, delayMs = 100)
// Returns: Promise<void>

static async tryUpdate(glueQuerySet, queryModelObject, field = null, maxRetries = 1, errorHelper = null, delayMs = 100)
// Returns: Promise<void>

static async tryMethod(glueQuerySet, id, method, kwargs = {}, maxRetries = 1, errorHelper = null, delayMs = 100)
// Returns: Promise<*>

static async tryNullObject(glueQuerySet, maxRetries = 1, errorHelper = null, delayMs = 100)
// Returns: Promise<ModelObjectGlue>

static async tryToChoices(glueQuerySet, filterParams = {}, maxRetries = 1, errorHelper = null, delayMs = 100)
// Returns: Promise<Array>
```
