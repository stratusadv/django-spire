# Progress

> **Purpose:** Track and stream real-time progress for multi-step background operations using Django's cache backend, with animated percent simulation and Server-Sent Event compatible output.

---

## Why Progress?

Long-running operations — imports, report generation, bulk processing — leave users waiting with no feedback. **The Progress system** provides:

- A `ProgressSession` that tracks one or more named tasks through their lifecycle
- Smooth progress simulation using an easing curve so the bar always appears to be moving
- A `stream()` generator that yields JSON snapshots for Server-Sent Events or polling endpoints
- `ParallelTask` for wrapping `concurrent.futures` futures with automatic completion tracking
- `SequentialTask` for executing callables synchronously with error capture and result access
- Django cache-backed persistence so progress is readable from any request context

---

## Quick Start

### 1. Create a Session

```python
from django_spire.contrib.progress.session import ProgressSession

session = ProgressSession.create(tasks={
    'import_products': 'Import Products',
    'update_prices': 'Update Prices',
})
```

`create()` stores the session in the Django cache and returns the `ProgressSession` instance. Pass the `session_id` to the client so it can poll for updates.

### 2. Run Tasks Against the Session

```python
# Sequential: executes immediately and blocks until done
task = session.add_sequential('import_products', import_products_from_csv, file_path)

# Parallel: wraps a future; completion is tracked on a daemon thread
future = executor.submit(fetch_price_data)
session.add_parallel('update_prices', future)
```

### 3. Stream Progress to the Client

```python
from django.http import StreamingHttpResponse

def progress_stream_view(request, session_id):
    session = ProgressSession.get(session_id)

    return StreamingHttpResponse(
        session.stream(),
        content_type='application/json',
    )
```

Each yielded chunk is a JSON string containing the overall percent, session status, and per-task details.

---

## Core Concepts

### `ProgressSession`

The central coordinator. Manages task state, drives progress simulation, persists to cache, and produces the stream.

```python
from django_spire.contrib.progress.session import ProgressSession
```

**Class methods:**

| Method | Description |
|---|---|
| `create(tasks)` | Create a new session. `tasks` is a `dict[str, str]` mapping task IDs to display names. Returns the session and saves it to cache. |
| `get(session_id)` | Load an existing session from cache. Returns `None` if the session has expired or does not exist. |

**Instance methods:**

| Method | Description |
|---|---|
| `add_sequential(task_id, func, *args, **kwargs)` | Execute `func` synchronously. Marks the task running, calls the function, then marks it complete or errored. Returns a `SequentialTask`. |
| `add_parallel(task_id, future)` | Wrap a `concurrent.futures` future. Marks the task running and monitors it on a daemon thread. Returns a `ParallelTask`. |
| `start(task_id)` | Mark a task as running and begin progress simulation. Called automatically by `add_sequential` and `add_parallel`. |
| `complete(task_id, message=None)` | Mark a task as completing. The simulation ticks the percent up to 100 then sets status to `COMPLETE`. |
| `error(task_id, message=None)` | Mark a task as errored and stop its simulation thread. |
| `stream(poll_interval=0.1)` | Generator that yields JSON snapshots at `poll_interval` seconds. Loops until all tasks are complete or any task has errored, then deletes the session from cache. |
| `to_dict()` | Return a snapshot of the current session state as a plain `dict`. |

**Properties:**

| Property | Type | Description |
|---|---|---|
| `has_error` | `bool` | `True` if any task has status `ERROR` |
| `is_complete` | `bool` | `True` if all tasks have status `COMPLETE` |
| `is_running` | `bool` | `True` if any task is `RUNNING` or `COMPLETING` |
| `overall_percent` | `int` | Average percent across all tasks |
| `status` | `ProgressStatus` | Aggregate status: `ERROR` > `COMPLETE` > `RUNNING` > `PENDING` |

### `ProgressStatus`

```python
from django_spire.contrib.progress.enums import ProgressStatus
```

| Value | Description |
|---|---|
| `PENDING` | Task has not started |
| `RUNNING` | Task is active and being simulated |
| `COMPLETING` | Task finished; simulation is ticking to 100% |
| `COMPLETE` | Task reached 100% |
| `ERROR` | Task raised an exception |

### `SequentialTask`

Executes a callable synchronously inside the progress session. If the callable raises, the task is marked errored and the exception is stored. Accessing `.result` re-raises the stored exception.

```python
from django_spire.contrib.progress.tasks import SequentialTask
```

| Member | Description |
|---|---|
| `.result` | Returns the callable's return value, or raises the stored exception if one occurred |

### `ParallelTask`

Wraps a `concurrent.futures.Future`. A daemon thread waits for `future.result` and marks the task complete or errored when it resolves.

```python
from django_spire.contrib.progress.tasks import ParallelTask
```

| Member | Description |
|---|---|
| `.result` | Proxies `future.result` — returns the future's value or raises its exception |

---

## Main Operations

### Running Sequential Tasks

```python
from django_spire.contrib.progress.session import ProgressSession

session = ProgressSession.create(tasks={
    'validate': 'Validate File',
    'import': 'Import Records',
})

validate_task = session.add_sequential('validate', validate_upload, file_path)

if validate_task.result:
    session.add_sequential('import', import_records, file_path)
```

Each call to `add_sequential` blocks until the callable returns, so tasks run one after the other in the order they are added.

### Running Parallel Tasks

```python
from concurrent.futures import ThreadPoolExecutor
from django_spire.contrib.progress.session import ProgressSession

session = ProgressSession.create(tasks={
    'fetch_orders': 'Fetch Orders',
    'fetch_inventory': 'Fetch Inventory',
})

with ThreadPoolExecutor() as executor:
    orders_future = executor.submit(fetch_orders_from_api)
    inventory_future = executor.submit(fetch_inventory_from_api)

    session.add_parallel('fetch_orders', orders_future)
    session.add_parallel('fetch_inventory', inventory_future)
```

Both tasks run concurrently. Each `ParallelTask` spawns a daemon thread that watches its future and reports completion back to the session.

### Retrieving a Session from Cache

```python
from django_spire.contrib.progress.session import ProgressSession

session = ProgressSession.get(session_id)

if session is None:
    # Session expired (default TTL is 300 seconds) or never existed
    ...
```

### Streaming Progress as JSON

```python
from django.http import StreamingHttpResponse
from django_spire.contrib.progress.session import ProgressSession

def report_progress_view(request, session_id):
    session = ProgressSession.get(session_id)

    if session is None:
        return HttpResponseNotFound()

    return StreamingHttpResponse(
        session.stream(poll_interval=0.2),
        content_type='application/json',
    )
```

Each streamed chunk is a newline-terminated JSON string. The client reads chunks until the session reports `complete` or `error`, at which point `stream()` stops and the cache entry is deleted.

### Reading a Progress Snapshot

```python
snapshot = session.to_dict()
# {
#     'overall_percent': 45,
#     'session_id': '...',
#     'status': 'running',
#     'tasks': {
#         'import_products': {
#             'message': 'Processing...',
#             'name': 'Import Products',
#             'percent': 45,
#             'status': 'running',
#         },
#         ...
#     }
# }
```

Note that `COMPLETING` status is reported as `'running'` in the serialised output — clients do not need to handle the intermediate completing state.
