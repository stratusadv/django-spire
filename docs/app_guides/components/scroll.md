# Scroll Components

> **Purpose:** Show an infinite list as a Glue component that loads its rows a batch at a time, updates one row at a time, and can create, edit and delete its rows.

---

## Why Scroll Components?

A list page usually needs the same things: load more rows as the user scrolls, reload when a search or filter changes, and redraw a row after it is edited. **The scroll components** provide:

- Paging on the server, one query per batch, with no position held between requests
- Rows drawn in the browser from data, or rendered on the server from a template
- Search and filter controls declared on the component and applied with one call
- Updates to a single row by key, from the browser or from a callable
- Ready-made create, edit and delete, each in a modal or on a page
- Lists of anything: a queryset, an API, or any source that can return a batch

They sit beside the older template scroll in `django_spire/glue/scroll/`, which is unchanged. See [Filtering](../core/filtering.md) for that one.

---

## Quick Start

### 1. Write the list component

```python
from django_spire.core.components import QuerySetScrollComponent

from app.task.models import Task


class TaskListComponent(QuerySetScrollComponent):
    item_template = 'task/item/task_row.html'
    view_template = 'django_spire/component/page/full_page.html'
    fields = ('name', 'status')

    def get_queryset(self):
        return Task.objects.active().order_by('name')
```

### 2. Write the row template

```html
--8<-- "docs/app_guides/components/templates/scroll_task_row.html"
```

### 3. Add a route

```python
from django.contrib.auth.decorators import login_required
from django.urls import path

from app.task.components import TaskListComponent

urlpatterns = [
    path('list/', login_required(TaskListComponent.as_view()), name='list'),
]
```

The page now lists the first 25 tasks and loads 25 more each time the user nears the bottom.

---

## Core Concepts

### `BaseScrollComponent`

The base of every scroll. It owns paging and all behaviour in the browser, and knows nothing about where its items come from. A subclass supplies the items through three methods.

```python
from django_spire.core.components import BaseScrollComponent
```

| Method | Description |
|---|---|
| `get_items(offset, limit)` | Return up to `limit` items starting at `offset`, in an order that is the same on every call |
| `get_item(key)` | Return the item with this key, or `None` when it no longer belongs in the list |
| `get_item_key(item)` | Return the value that identifies an item among all items |

| Setting | Description |
|---|---|
| `template` | The list's template. It must extend `django_spire/component/scroll/base.html` |
| `item_template` | The markup for one row |
| `item_render_mode` | Where a row is drawn. A `ScrollItemRenderMode`, `CLIENT` by default |
| `batch_size` | How many rows are loaded at a time. Defaults to `25` |
| `view_template` | The page the component is shown in when served by `as_view()` |

A subclass that overrides `__post_init__(self, request)` must call `super().__post_init__(request)`. The base refuses to run without it.

### `ScrollItemRenderMode`

Says where a row is drawn. `item_template` is the row in both modes, but it is written differently for each.

```python
from django_spire.core.components import ScrollItemRenderMode
```

| Member | Rows are | The row template |
|---|---|---|
| `CLIENT` | Sent as data and drawn in the browser | Uses Alpine attributes that read `item`. Optional: a list may fill the `scroll_item` block of its own template instead |
| `SERVER` | Rendered on the server and sent as HTML | Uses Django tags. Required, and must extend `item.html` or `table_row.html` |

A row template written for one mode is refused in the other, when the component is first used.

### `QuerySetScrollComponent`

A scroll over the rows of a queryset. It fills in the three item methods, so a subclass writes `get_queryset()`.

```python
from django_spire.core.components import QuerySetScrollComponent
```

| Member | Description |
|---|---|
| `get_queryset()` | Return the rows the list shows, in the order it shows them |
| `fields` | The fields each row carries to the browser in `CLIENT` mode, beside `pk` |
| `get_instance(pk)` | Return one row of the queryset for a callable that acts on it. A row outside the list is reported as a 404 |

The primary key is added to the end of the queryset's ordering, so rows that tie on the ordering never repeat or go missing between batches. A queryset with no ordering is listed by primary key.

In `CLIENT` mode an item is a dict of `pk` and `fields`. In `SERVER` mode it is the model instance.

### `GlueScrollItemsMixin`

Sends each row to the browser as a Glue model instead of a dict, so the row's markup can call the model's Glue methods and save its fields. List it ahead of a queryset scroll.

```python
from django_spire.core.components import GlueScrollItemsMixin
```

| Member | Description |
|---|---|
| `fields` | The fields each Glue model exposes |
| `get_glue_item(item, name, **kwargs)` | Build the Glue model for one row. Override it to pass further `Glue.model` options, such as a `form` |

It applies to `CLIENT` mode only. A Glue row costs more to send than a dict, so use it for lists whose rows are edited in place.

### `ModelCrudScrollComponent`

A queryset scroll with create, edit and delete.

```python
from django_spire.core.components import ModelCrudScrollComponent
```

| Setting | Description |
|---|---|
| `item_form_options` | How a row is created and edited. `None`, the default, means the list has neither |
| `item_delete_options` | How a row is deleted. The default is a confirmation that soft-deletes. `None` turns deleting off |

Only rows in `get_queryset()` can be edited or deleted, and each action checks the user's access.

### Form and delete options

Each action happens in a component shown in a modal, or on a page. The class of the options object says which.

```python
from django_spire.core.components import (
    ComponentDeleteOptions,
    ComponentFormOptions,
    PageDeleteOptions,
    PageFormOptions,
)
```

| Options | Arguments | Description |
|---|---|---|
| `ComponentFormOptions` | `component`, or `form_class` with `template` | A form component in a modal. See [Form Components](form.md) |
| `PageFormOptions` | `url_name`, `create_url_name`, `return_url_name` | A form page. `url_name` takes the row's key as `pk` |
| `ComponentDeleteOptions` | `component` | A confirmation in a modal. See [Confirmation Components](confirmation.md) |
| `PageDeleteOptions` | `url_name`, `return_url_name` | A delete page. `url_name` takes the row's key as `pk` |

With `PageFormOptions`, creating goes to `create_url_name`, or to `url_name` with a `pk` of `0` when that is left out.

A page link carries a `return_url` query parameter: the route named by `return_url_name`, or the address the list is shown at. A page that reads `return_url` sends the user back there afterwards.

### Templates

| Template | Description |
|---|---|
| `django_spire/component/scroll/base.html` | The list. Every list template extends it, directly or through one of the next two |
| `django_spire/component/scroll/table.html` | The list as a table |
| `django_spire/component/scroll/crud.html` | The list with create, edit and delete |
| `django_spire/component/scroll/item.html` | One server-rendered row, as a `div` |
| `django_spire/component/scroll/table_row.html` | One server-rendered row, as a `tr` |
| `django_spire/component/page/full_page.html` | A full page that shows one component |

| Block | In | Description |
|---|---|---|
| `scroll_header` | `base.html` | Markup above the rows, such as a search box or a New button |
| `scroll_item` | `base.html` | One row in `CLIENT` mode. Draws `item_template` unless overridden |
| `scroll_empty` | `base.html` | What is shown when the list has no rows |
| `scroll_loading` | `base.html` | What is shown while a batch loads |
| `scroll_footer` | `base.html` | Markup below the rows |
| `scroll_container_class` | `base.html` | Classes on the list's outer element |
| `scroll_table_header` | `table.html` | The table's header row |
| `scroll_table_class` | `table.html` | Classes on the `table` |
| `scroll_item_content` | `item.html`, `table_row.html` | The content of one server-rendered row |
| `scroll_item_class` | `item.html`, `table_row.html` | Classes on one server-rendered row |

### In the browser

Markup inside the list can read the list's state and call its methods.

| Name | Description |
|---|---|
| `items`, `keys` | The rows shown and their keys, in `CLIENT` mode |
| `loadedCount` | How many rows are shown |
| `hasMore` | Whether another batch may exist |
| `isLoading` | Whether a batch is loading |
| `reloadItems()` | Send the controls to the server and show the first batch again |
| `addItem(key)` | Fetch one row and put it at the top |
| `refreshItem(key)` | Fetch one row again and redraw it. A row the server no longer has is removed |
| `removeItem(key)` | Take one row out of the list |
| `createItem()`, `editItem(item)`, `deleteItem(item)` | The CRUD actions. Each of the last two takes the item or its key |

---

## Main Operations

### Rendering Rows on the Server

```python
from django_spire.core.components import QuerySetScrollComponent, ScrollItemRenderMode


class TaskListComponent(QuerySetScrollComponent):
    item_render_mode = ScrollItemRenderMode.SERVER
    item_template = 'task/item/task_row.html'

    def get_queryset(self):
        return Task.objects.active().order_by('name')
```

```html
--8<-- "docs/app_guides/components/templates/scroll_task_row_server.html"
```

The row template extends `item.html`, which gives the row the attribute the list finds it by. The row receives `item`, the model instance, so it can use anything a Django template can, such as `get_status_display`.

### Listing as a Table

```python
class TaskTableComponent(QuerySetScrollComponent):
    template = 'task/component/task_table.html'
    item_render_mode = ScrollItemRenderMode.SERVER
    item_template = 'task/item/task_table_row.html'

    def get_queryset(self):
        return Task.objects.active().order_by('name')
```

```html
--8<-- "docs/app_guides/components/templates/scroll_task_table.html"
```

```html
--8<-- "docs/app_guides/components/templates/scroll_task_table_row.html"
```

The list template extends `table.html` and fills in the header. The row extends `table_row.html`. The two row templates share their block names, so a row moves between a `div` and a `tr` by changing only the template it extends.

### Adding Search and Filters

```python
from django_glue import Glue

from app.task.choices import TaskStatusChoices


class TaskListComponent(QuerySetScrollComponent):
    template = 'task/component/task_list.html'
    item_template = 'task/item/task_row.html'
    fields = ('name', 'status')

    status_choices = tuple(TaskStatusChoices.choices)

    search: str = Glue.attr('', editable=True)
    status: str = Glue.attr('', editable=True)

    def get_queryset(self):
        queryset = Task.objects.active().search(self.search)

        if self.status in TaskStatusChoices.values:
            queryset = queryset.filter(status=self.status)

        return queryset.order_by('name')
```

```html
--8<-- "docs/app_guides/components/templates/scroll_task_list_with_search.html"
```

A control is an editable attribute on the component. The markup binds an input to it, and `reloadItems()` sends its value to the server and shows the first batch again. The component reads the value where it builds its queryset. Check a value against what is allowed before using it, as `status` is here, because it comes from the browser.

### Acting on a Row From a Callable

```python
class TaskListComponent(QuerySetScrollComponent):
    item_template = 'task/item/task_row.html'
    fields = ('name', 'status')

    def get_queryset(self):
        return Task.objects.active().order_by('name')

    @Glue.attr(required_access=Glue.Access.CHANGE, skip_rerender=True)
    def complete(self, pk: int) -> None:
        self.get_instance(pk).services.processor.complete()
        self.item_changed(key=pk)
```

```html
--8<-- "docs/app_guides/components/templates/scroll_task_row_with_action.html"
```

`get_instance(pk)` looks the row up inside the list's own queryset, so a callable cannot reach a row the list does not show. `skip_rerender=True` stops the whole list from being redrawn, and firing `item_changed` redraws that one row. Fire `item_added` or `item_removed` in the same way for a row that was created or taken away.

The button is an [async button](async_button.md), so a second click sends nothing while the first is running.

### Creating, Editing and Deleting

```python
from django_spire.core.components import (
    ComponentFormOptions,
    ModelCrudScrollComponent,
)

from app.task.forms import TaskForm


class TaskListComponent(ModelCrudScrollComponent):
    template = 'task/component/task_list.html'
    item_template = 'task/item/task_row.html'
    fields = ('name', 'status')

    item_form_options = ComponentFormOptions(
        form_class=TaskForm,
        template='task/form/task_form.html',
    )

    def __post_init__(self, request):
        super().__post_init__(request)

        if request.user.has_perm('task.delete_task'):
            self.access = Glue.Access.DELETE
        elif request.user.has_perm('task.change_task'):
            self.access = Glue.Access.CHANGE

    def get_queryset(self):
        return Task.objects.active().order_by('name')
```

```html
--8<-- "docs/app_guides/components/templates/scroll_task_crud_list.html"
```

```html
--8<-- "docs/app_guides/components/templates/scroll_task_crud_row.html"
```

The list template extends `crud.html`, which adds `createItem()`, `editItem(item)` and `deleteItem(item)`. With these options the form opens in a modal and the new or changed row appears in the list when it is saved. Deleting asks for confirmation and soft-deletes the row.

Creating and editing need `CHANGE` access and deleting needs `DELETE`. A component starts with `VIEW`, so set `self.access` from what the user may do.

### Using Pages for the Form or the Delete

```python
from django_spire.core.components import PageDeleteOptions, PageFormOptions


class TaskListComponent(ModelCrudScrollComponent):
    item_form_options = PageFormOptions('task:form:update', create_url_name='task:form:create')
    item_delete_options = PageDeleteOptions('task:form:delete')
```

The same three methods then send the user to those pages. Use this when the app already has form and delete views. Each link carries `return_url`, so a view that reads it brings the user back to the list.

### Deleting Another Way

```python
from django_spire.core.components import (
    BaseModelDeleteConfirmationComponent,
    ComponentDeleteOptions,
    ModelDeleteConfirmationComponent,
)


class TaskArchiveConfirmationComponent(BaseModelDeleteConfirmationComponent):
    def perform_action(self) -> None:
        self.instance.services.processor.archive()


class TaskListComponent(ModelCrudScrollComponent):
    item_delete_options = ComponentDeleteOptions(component=TaskArchiveConfirmationComponent)


class AuditLogListComponent(ModelCrudScrollComponent):
    item_delete_options = ComponentDeleteOptions(component=ModelDeleteConfirmationComponent)
```

The first list deletes through its own confirmation. The second deletes the row from the database, where the default only marks it deleted. Set `item_delete_options = None` for a list that cannot delete.

### Editing a Row in Place

```python
from django_spire.core.components import GlueScrollItemsMixin, QuerySetScrollComponent


class TaskListComponent(GlueScrollItemsMixin, QuerySetScrollComponent):
    item_template = 'task/item/task_row.html'
    fields = ('name', 'status')

    status_choices = tuple(TaskStatusChoices.choices)

    def get_queryset(self):
        return Task.objects.active().order_by('name')

    def get_glue_item(self, item, name, **kwargs):
        return super().get_glue_item(item, name, form=TaskForm, **kwargs)
```

```html
--8<-- "docs/app_guides/components/templates/scroll_task_glue_row.html"
```

Each row is a Glue model with the form attached. The select is bound to the row's form, and changing it saves through the form's own method, which runs the form's validation and the application's save. The row's key is `item.$pk`.

### Listing Something That Is Not a Queryset

```python
from django_spire.core.components import BaseScrollComponent, ScrollItemRenderMode


class CustomerListComponent(BaseScrollComponent):
    item_render_mode = ScrollItemRenderMode.SERVER
    item_template = 'customer/item/customer_row.html'

    def get_items(self, offset, limit):
        return crm_client.customers(skip=offset, limit=limit)

    def get_item(self, key):
        return crm_client.customer(key)

    def get_item_key(self, item):
        return item.id
```

Pass `offset` and `limit` on to the source so that each batch is one request to it. Return `None` from `get_item` for an item the source no longer has, and the list removes its row.

### Testing a List

```python
from django_spire.testing.playwright import ScrollComponent


def test_scrolling_loads_every_task(page, demo_start):
    demo_start().goto('task:page:list')

    scroll = ScrollComponent(page, row_selector='[data-task-row]')
    scroll.scroll_until_row_count(60)

    assert scroll.state()['hasMore'] is False
```

`ScrollComponent` is a Playwright helper that waits on the list's own state, so a test never sleeps. Give it a selector that matches one row of the list under test.

---

## Things to Know

- **A project that does not extend Spire's `base.html`** must load the scripts in `django_spire/js/components/` itself.
- **A form or a confirmation acts on the row it was opened for.** The list checks that the row is in its queryset when the prompt opens, and not again when the user saves or confirms. A list whose queryset is a permission rule should scope the lookup in its own component. See [Confirmation Components](confirmation.md).
- **Paging is by offset.** A row inserted while a user scrolls can make a row repeat or be skipped. Reloading the list corrects it.
