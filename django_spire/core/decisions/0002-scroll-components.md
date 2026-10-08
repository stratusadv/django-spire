# Scroll components page on the server and update rows by key

Status: Accepted

Date: 2026-10-08

## Context

`django_spire/glue/scroll/scroll.html` shows an infinite list by extending a
template and naming a Glue queryset registered in a view (ADR 0001). Three
things about it could not be changed from application code:

- **The items had to be a Glue queryset.** Search hits, API results and merged
  lists could not be scrolled.
- **The controls were fixed.** One search box bound to one `icontains` lookup,
  one ordering field. A search across two fields, or a status filter, meant
  replacing the template's logic.
- **The wiring lived in each consumer.** A view registered the queryset under a
  unique name, the template repeated that name, and a row update travelled as a
  window-level `updated-item` event.

Glue 1.2 components carry their own state, callables and events, which made a
component the natural owner of all three.

## Decision

A new family of components in `django_spire.core.glue.components.scroll`,
beside the template scroll, which is unchanged.

**The base is agnostic about its items.** A `BaseScrollComponent` subclass
supplies `get_items(offset, limit)` in a stable order, `get_item(key)` and
`get_item_key(item)`. The base owns paging and every client behaviour.

**The server holds no position.** The client sends the number of rows it
holds. The base asks for `batch_size + 1` items, trims, and reports whether
there are more. The limit never comes from the client.

**Rows are rendered one of two ways.** With `item_template` set, each item is
rendered on the server and a batch arrives as HTML. Left unset, items are sent
as data and rendered by the `scroll_item` block. This is one branch in the base
and its template, taken deliberately: making rendering a class would cross it
with the item source and need a class for each pair.

**Controls belong to the application.** A subclass declares any it wants as
editable attributes and reads them where it selects its items. A control
change calls `reloadItems()`, which refreshes the component and shows the first
batch again. The base has no notion of search or ordering.

**One row changes at a time, by key.** The template has `addItem(key)`,
`refreshItem(key)` and `removeItem(key)`, and the component declares
`item_added`, `item_changed` and `item_removed`. An event carries only the key,
and the client fetches that one row. Carrying the rendered row in the event
would save a request, but fails for a row that contains a component, whose
registration data travels with HTML responses and not inside an event.

**Loads are ordered by generation**, as in ADR 0001. A batch or first batch
that finishes after a newer reload began is discarded.

**`QuerySetScrollComponent`** takes its items from `get_queryset()`. It refuses
an unordered queryset and appends the primary key to the ordering, so that the
order is total and offsets are stable. Data rows are dicts of `pk` and
`fields`.

**`GlueScrollItemsMixin`** sends each item as a Glue object, so the row markup
can call a model's Glue methods and services and save its fields with no
callable on the component. A load returns a `SequenceGlue` of up to
`batch_size + 1` rows; the extra one says there is more, because Glue does not
allow Glue objects inside a plain result. Each row is named from its key, which
is how the client reads the key back. The client disposes each batch once it
has taken the rows out, and each row it later drops.

**Glue rows never arrive with the render.** Glue does not run a child-producing
property again when its component refreshes (django-glue state-model.md §10),
so a first batch held in a property would never follow a control change. Every
batch comes from the `load_items` callable, and a reload is a refresh followed
by a load.

**`ModelCrudScrollComponent`** adds ready-made actions. `item_form_options`
says how a row is created and edited: `ComponentItemFormOptions` shows a form
component in a modal, and `PageItemFormOptions` sends the user to a page.
`delete_component` is the confirmation shown before a row is deleted. The
template's `createItem()`, `editItem(item)` and `deleteItem(item)` perform them
and take the item or its key. Only rows in `get_queryset()` can be edited or
deleted. The helpers use only the scroll's public callables and row operations,
so an application can replace any of them or do the same work by hand.

## Alternatives considered

- **Own a Glue queryset as a child, and page it from the client.** This gives
  rows their proxies for free. Glue signs a child queryset when it is first
  introduced, so server-side controls did not reach it, and client filtering
  is limited to allow-listed field lookups, which is the restriction this work
  set out to remove. A second query view also disposed the rows of the first.
- **An opaque cursor in place of an offset.** Every subclass would encode and
  decode a token to say "the next 25".
- **Ask Glue to run the first-batch property again on refresh.** The server
  accepts a `reintroduce` list, but the client does not expose it, and a
  reintroduced sequence did not register its rows. Measured against a refresh
  followed by a load, it would save one round trip per reload.
- **Keep the first batch of Glue rows in a property.** A refresh then resends
  about 3.8 KB per row whether or not the rows changed, against a flat 3.3 KB
  without the property.
- **A class or an object for each form placement.** A list's form settings went
  through several shapes: loose class variables with guards, a mode enum, and
  one object per action. Two option classes replaced them, because they make an
  invalid combination impossible to write or refuse it where it is built.

## Consequences

- A Glue row costs about 2.9 KB with three fields, and about 6.6 KB with a form
  attached, against a small fraction of that for a dict. A list opts in with
  the mixin.
- A reload of Glue rows is two requests. Dict and server-rendered reloads are
  one.
- Offset paging can repeat or skip a row when rows are inserted while a user
  scrolls. Continuation paging (ADR 0001) does not, and stays available in the
  template scroll.
- `base.html` has a `scroll_data` block at the end of its Alpine data, which is
  how `crud.html` adds its helpers. A template that adds its own keeps them with
  `{{ block.super }}`.
- The sizes and timings above come from single runs on one machine and are
  indicative. Database queries were counted in tests, not in those runs.
- Supporting components were added or changed for this: `BaseConfirmationComponent`
  and `ModelDeleteConfirmationComponent`, and a rework of the form components so
  that one can be built from a form class and a template without a subclass.
- Not built: showing the form inline in a row, a form component that renders
  any form's fields without a template, and deriving a list's access from the
  user's permissions.
- Coverage:
  - `django_spire/core/glue/components/tests/test_scroll/` tests each class,
    including one query per batch at any offset and one per single row.
  - `test_project/app/history`, `rest`, `comment`, `ordering` and `task` each
    hold a demo and its browser tests: a read-only list, a table with search,
    page-mode forms on one route and on two, and Glue rows with modal forms,
    nested lists and a disposal check across reloads.
