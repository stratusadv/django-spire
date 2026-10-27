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

**Rows are rendered on the server.** `item_template` is the markup for one row,
written with Django tags, and a batch arrives as HTML. The row receives the
item itself, so it can use model methods, related objects and `{% url %}`, and
Alpine attributes in it still reach the list and the component. The only rows
drawn in the browser are Glue rows (below), because only a row that edits
itself in place needs to be data in the browser. Plain data rows were
considered and left out: everything they show, a server row shows too, and
each list would have had to choose between two ways of writing the same
read-only row. A row template is written for one of the two, Django tags for
the server and Alpine attributes for Glue rows, and the base refuses one used
for the other.

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

**`QuerySetScrollComponent`** takes its items from `get_queryset()`. It
appends the primary key to the queryset's ordering, so that the order is total
and offsets are stable. An unordered queryset is therefore listed by primary
key. Each item is a model instance. `get_instance(pk)` returns one
row of the queryset for a callable that acts on it, and reports a row outside
the list as Glue's 404.

**Glue rows are one setting on the queryset scroll.** `glue_items = True`
sends each row as the Glue model the list's `get_glue_item(item, name)` builds,
and a list that sets it without overriding the hook is refused when it is
defined. There is no default build from a list of fields: the hook is where a
list states exactly what a row exposes, its fields, access and form, since a
row with `CHANGE` access can save those fields from the browser. The row
markup can call a model's Glue methods and services and save its fields with
no callable on the component.

Glue fixes whether a callable returns Glue objects from its return annotation,
when the class is defined, so one callable cannot return HTML for one list and
Glue models for another. Glue rows therefore have their own pair,
`load_glue_items` and `load_glue_item`, beside `load_items` and `load_item`.
Every queryset scroll declares all four, the template tells the client which
pair to call, and each pair refuses to run on a list whose rows are the other
kind. The Glue pair stays off `BaseScrollComponent`, since its rows are model
instances. A load returns
a `SequenceGlue` of up to `batch_size` rows, and a full batch means there may
be more, because Glue does not allow Glue objects inside a plain result to say
so. A list whose length is an exact multiple of the batch size makes one empty
request at its end. Each row is named from its key, so that names are unique,
and the client reads the key from the Glue model's own `$pk`. The client keeps
each batch for as long as its rows are shown, because a row's address is
derived from its batch's and is disposed with it. A reload releases the
previous batches and rows, and a single row that is removed or replaced is
released on its own, in each case after Alpine has stopped rendering it.

**Glue rows never arrive with the render.** Glue does not run a child-producing
property again when its component refreshes (django-glue state-model.md §10),
so a first batch held in a property would never follow a control change. Every
batch comes from the `load_glue_items` callable, and a reload is a refresh
followed by a load.

**`ModelCrudScrollComponent`** adds ready-made actions. `item_form_options`
says how a row is created and edited: `FormOptions` shows a form component in
a modal, and `PageFormOptions` sends the user to a page.
`item_delete_options` says how a row is deleted in the same two ways:
`DeleteOptions` shows a confirmation component in a modal, which soft-deletes
by default, and `PageDeleteOptions` sends the user to a delete page, so a list
can use the delete view its app already has. The kind of options object is the
mode, so there is no mode setting that could disagree with the others. The
modal is the plain name because it is the list's own flow, and the page is the
named variant. The four classes are defined in the form and confirmation
packages, beside the components they build, and `ModelCrudScrollComponent`
carries them as class attributes, so a list writes
`ModelCrudScrollComponent.FormOptions(...)` with nothing else to import. A page link carries a `return_url`, the route named by
`return_url_name` or else the address the list is shown at, which a page
following Spire's convention sends the user back to.

The template's `createItem()`, `editItem(item)` and `deleteItem(item)` perform
the actions and take the item or its key. The browser fetches the modal
components with the `load_item_form` and `load_item_delete_confirmation`
callables, named like `load_items` and `load_item`: a `load_` method is what
the browser calls, and a `get_` method is what an application overrides. The
`load_` callables check the user's access and that the row is in
`get_queryset()`, so an action is customised through the two settings and the
queryset, which keep those checks, and not by overriding the callables.

**A prompt acts on the row it was opened for.** A form or confirmation is
built after the list has checked that the row is in its queryset, and Glue
signs the row's key for that user and session for 24 hours. The check is not
repeated when the user saves or confirms, so a row that leaves the queryset
while a prompt is open can still be acted on from that prompt. A list whose
queryset is a permission rule scopes the lookup in its own form or
confirmation component.

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
  one object per action. Two option classes for the form, and two for delete,
  replaced them, because they make an invalid combination impossible to write
  or refuse it where it is built.
- **Named constructors or a builder for the options**, such as
  `FormOptions.page(...)`. Each would be a one-line pass-through to a
  constructor that already takes keyword arguments, on a base class that names
  its own subclasses.
- **A mixin for Glue rows**, supplying Glue versions of `load_items` and
  `load_item`. It worked only when listed ahead of the scroll class, and listed
  after it the list silently sent HTML. It also needed its own checks that it
  sat on a queryset scroll and not on one rendered on the server.
- **Rewriting the loads when the class is defined**, so that one pair of
  callables could follow the setting. It fights how Glue reads a callable's
  return type, and is harder to follow than a second pair.
- **Deciding Glue rows without a setting**: from whether the row template
  extends a server row template, from whether `get_glue_item()` is overridden,
  or from a non-empty list of fields. Each makes the choice to put live,
  possibly editable models in the browser a side effect of something else, and
  a slip in the template or the class would switch it silently.
- **Plain data rows drawn in the browser**, as a third kind beside server rows
  and Glue rows. They cost less to send than either, but show nothing a server
  row cannot, and only the columns they list. The smaller payload did not
  justify a second way to write a read-only row.
- **Hooks for building the form and confirmation components.** Nothing passes
  parameters from a list into the component it opens yet. When something does,
  the hook is a `get_` method the `load_` callable calls.
- **Repeating the queryset check when a prompt is confirmed**, by fingerprinting
  the row or expiring the prompt. The window is narrow and bounded by Glue's
  token, and the lists it matters for can scope their own lookup.

## Consequences

- A Glue row costs about 2.9 KB with three fields, and about 6.6 KB with a form
  attached, against the HTML of a server-rendered row. A list opts in with
  `glue_items`.
- Every queryset scroll declares four load callables, two of which refuse to
  run for that list, and a Glue list writes its own `Glue.model(...)` call in
  `get_glue_item()`.
- A reload of Glue rows is two requests. A server-rendered reload is one.
- A server row can read related objects, so a list that shows them loads them
  in `get_queryset()` with `select_related` or `prefetch_related` to keep a
  batch at one query.
- Offset paging can repeat or skip a row when rows are inserted while a user
  scrolls. Continuation paging (ADR 0001) does not, and stays available in the
  template scroll.
- The scroll's client behaviour is two Alpine components in
  `django_spire/js/components/scroll.js`, not script in the template, so a list
  renders only its markup. `scroll.html` names its component in the
  `scroll_data_name` block and passes it options in `scroll_options`, which is
  how `crud_scroll.html` swaps in `crudScrollComponent` and its page URLs. A project
  that does not extend Spire's `base.html` loads that script itself.
- The sizes and timings above come from single runs on one machine and are
  indicative. Database queries were counted in tests, not in those runs.
- Supporting pieces were added or changed for this: `BaseConfirmationComponent`
  and the model action and delete confirmations built on it, a rework of the
  form components so that one can be built from a form class and a template
  without a subclass, the `asyncButton` Alpine component, and
  `django_spire/component/page/full_page.html` for serving a component as a
  page.
- Up to django-glue 1.2.1 the client disposed a record's children by an owner
  link that was only set once a child was read, so a Glue row dropped before
  its form was read left the form's record behind, and disposing a batch left
  its rows alive. django-glue 1.2.2 disposes children by their derived address.
  The scroll is written for that rule and also behaves correctly under the
  older one: it never drops a row it has not rendered, which is one reason a
  batch carries no extra row to signal that there is more, and it releases
  rows individually as well as by batch.
- Not built: a form component that renders any form's fields without a
  template, and deriving a list's access from the user's permissions.
- Coverage:
  - `django_spire/core/components/tests/` tests each class in `test_scroll/`,
    `test_form/` and `test_confirmation/`, including one query per batch at any
    offset and one per single row.
  - `test_project/app/history`, `rest`, `comment`, `ordering` and `task` each
    hold a demo and its browser tests: a read-only list, a table with search,
    page-mode forms on one route and on two, a custom delete, a delete page,
    async buttons, and Glue rows with modal forms, nested lists and a disposal
    check across reloads.
  - `rest` also lists pirates from the DummyJSON API on `BaseScrollComponent`
    directly, passing each batch's offset and limit to the API. Its tests
    replace the API, so they do not use the network; the page itself does.
