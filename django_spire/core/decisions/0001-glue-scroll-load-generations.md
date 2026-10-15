# Glue scroll pages by continuation and orders its loads

Status: Accepted

Date: 2026-09-28

## Context

`django_spire/glue/scroll/scroll.html` and its notification copy
(`django_spire/notification/app/scroll/scroll.html`, which also renders each row
through server templates) show an infinite list from a Glue queryset. Before
this decision each page was a separate `slice(start, stop)` query tracked by a
client cursor (`sliceStart` / `sliceStop` / `increment`), and loads were
unordered. That produced two classes of defect under Glue 1.1.

**Pages replaced each other.** In Glue 1.1 a query without a continuation key
*replaces* the queryset's loaded window (`WindowChange.REPLACED`). Every
`slice()` page was such a query, so each page load made the previous page's
rows leave the window. The client then disposed those rows' addressed
children, including the collection-owned relation children that projected
fields such as `item.partner.name` read (state-model.md §4, §10). Rows that
were still on screen showed `null` relations and raised template errors. On
the portal project list, scrolling left all 100 loaded rows with a `null`
partner.

**Loads raced.** `loadMoreItems()` and `resetAndLoad()` both mutate `items` and
the paging state across an `await`, and only an `isLoading` flag stood between
them:

1. *Overtaken reset.* Consumer filter handlers often call `resetAndLoad()`
   directly *and* change `searchQuery`, which triggers a second reset through
   the watcher. When the first reset finished during the second reset's
   `refresh()` await, it advanced the cursor. The second reset then loaded the
   second page of the filtered result and replaced the list with it, usually
   with nothing.
2. *Stale page over a reset.* A sentinel page load still in flight when the order
   or search changed made the reset's own load return early on `isLoading`.
   The stale page then landed on the cleared list.

The races date from Spire 1.0.1. The window replacement only became visible
with Glue 1.1's addressed relation children. Portal e2e tests found both: the
partner list's filter and sort tests failed in about a third of runs, and
walking the portal lists past their first page showed the `null` relations.

## Decision

**Page through the queryset's continuation.** A reset builds the filtered and
ordered view from `scrollQuerySet` and runs `refresh()` on it. This is one
request that returns the first batch and ignores any page cached from an
earlier load. Scrolling calls `loadMore()` on that same view, which follows
the signed continuation and *extends* the window, so loaded rows and their
relation children stay live. `hasMore` is the view's `hasNext`. Page size is
the Glue queryset's `batch_size` (`DJANGO_GLUE_QUERYSET_BATCH_SIZE` by default),
set on the view with the other queryset configuration. The template's
`increment` block and client cursor are removed.

**Order loads by generation.** Every reset starts a new `loadGeneration` and
marks the component loading before its request, so the sentinel cannot start
a competing first load. A load that finishes after a newer generation has
started discards its result, and leaves `items`, `hasMore`, and `isLoading` to
the newer load. The notification scroll checks the generation after both of
its awaits: the page, and the rendered templates.

Consumers keep calling `resetAndLoad()` however they like. Redundant triggers
are harmless.

## Alternatives considered

- **Keep `slice()` pages and fix relations in Glue.** Glue would have to keep
  children of rows that a replacing query removed from the window, which is the
  opposite of the window contract in state-model.md §10.
- **Remove the duplicate triggers in consumer templates.** This fixes only the
  filter race, and requires every consumer to know the rule.
- **Cancel superseded requests.** The Glue queryset proxy has no cancellation
  API, and an already-delivered response would still need the generation check.
- **Queue loads in order.** Correct, but users would wait for requests whose
  results are discarded.

## Consequences

- Continuation paging depends on Glue signing its seek keys and reading
  ordering values through relations. The notification list orders by
  `-notification__sent_datetime`. Both changes ship in django-glue 1.1.0
  (Glue ADR 017).
- Views that relied on Spire's 25-row page now receive Glue's batch size. The
  notification list and dropdown set `batch_size=25` to keep their page size.
- A superseded request still reaches the server; only its result is dropped.
- Regression coverage:
  - `test_project/app/task/tests/test_scroll_e2e.py` forces both load races
    deterministically.
  - `django_spire/notification/app/tests/test_scroll_e2e.py` covers the
    notification races, and walks every batch to check that each row keeps its
    related notification.
  - The portal partner, project, and environment list e2e tests cover consumer
    filters, sorting, and scrolling past the first batch.
