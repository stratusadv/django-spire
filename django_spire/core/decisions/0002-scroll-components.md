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

A new family of components in `django_spire.core.components.scroll`,
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
`batch_size` rows, and a full batch means there may be more, because Glue does
not allow Glue objects inside a plain result to say so. A list whose length is
an exact multiple of the batch size makes one empty request at its end. Each
row is named from its key, which is how the client reads the key back. The
client keeps each batch for as long as its rows are shown, because a row's
address is derived from its batch's and is disposed with it. A reload releases
the previous batches and rows, and a single row that is removed or replaced is
released on its own, in each case after Alpine has stopped rendering it.

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
- **A placement that opens the form inside the row.** It needed a special row
  template and client-side swapping for Alpine rows, a different mechanism for
  server-rendered rows, and a `cancelled` event on every form component, and
  nothing needed it. Glue rows already edit in place: a row given a form binds
  its inputs to `item.form` and saves through it. A row with state of its own
  can be a component.
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
- The scroll's client behaviour is two Alpine components in
  `django_spire/js/components/scroll.js`, not script in the template, so a list
  renders only its markup. `base.html` names its component in the
  `scroll_data_name` block and passes it options in `scroll_options`, which is
  how `crud.html` swaps in `crudScrollComponent` and its page URLs. A project
  that does not extend Spire's `base.html` loads that script itself.
- The sizes and timings above come from single runs on one machine and are
  indicative. Database queries were counted in tests, not in those runs.
- Supporting components were added or changed for this: `BaseConfirmationComponent`
  and `ModelDeleteConfirmationComponent`, and a rework of the form components so
  that one can be built from a form class and a template without a subclass.
- Up to django-glue 1.2.1 the client disposed a record's children by an owner
  link that was only set once a child was read, so a Glue row dropped before
  its form was read left the form's record behind, and disposing a batch left
  its rows alive. django-glue 1.3.0 disposes children by their derived address.
  The scroll is written for that rule and also behaves correctly under the
  older one: it never drops a row it has not rendered, which is one reason a
  batch carries no extra row to signal that there is more, and it releases
  rows individually as well as by batch.
- Not built: a form component that renders any form's fields without a
  template, and deriving a list's access from the user's permissions.
- Coverage:
  - `django_spire/core/components/tests/test_scroll/` tests each class,
    including one query per batch at any offset and one per single row.
  - `test_project/app/history`, `rest`, `comment`, `ordering` and `task` each
    hold a demo and its browser tests: a read-only list, a table with search,
    page-mode forms on one route and on two, and Glue rows with modal forms,
    nested lists and a disposal check across reloads.
  - `rest` also lists pirates from the DummyJSON API on `BaseScrollComponent`
    directly, passing each batch's offset and limit to the API. Its tests
    replace the API, so they do not use the network; the page itself does.
