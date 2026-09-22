# Metric Visual — Behavior Notes & Plan

Working notes on how `django_spire/metric/visual` behaves today, where behavior diverges
from expectation, and the planned changes.

## 1. How it works today

### Data model (`django_spire/metric/visual/models.py`)

- `Visual` — name, description, optional `Statistic` FK, `date` (evaluation date,
  defaults to today, **editable**), `kind` (indicator | line | bar | area | pie | gauge).
  One proxy model + service per kind (`IndicatorVisual`, `LineChartVisual`, ...).
- `VisualCondition` — ordered rule: `state` (green/blue/yellow/grey/red),
  `operator` (gt/gte/lt/lte/eq/between), `target`, `tolerance`, `order`.
- `VisualReference` — LIKE-style pattern (`%`/`_`) + label + order; selects which of the
  statistic's `reference` values become named datasets (series / pie slice / gauge).
- `VisualRegion` — unique slot key (e.g. `home:dashboard:hero`), optional visual,
  `is_live_updated`, title. Slot keys come from the
  `DJANGO_SPIRE_METRIC_VISUAL_REGIONS` setting.

### Value computation (`services/transformation_service.py`)

Everything is anchored to `visual.date` (the "Evaluation Date"), not necessarily now.

- **Period** = the statistic's interval around `visual.date`
  (`domain/statistic/interval.py`): daily → that day, weekly → Mon–Sun, monthly →
  calendar month.
- **Current value** (big header number):
  - no statistic / soft-deleted statistic → `0`
  - percentage statistics → moving-window **average of daily averages**, window =
    2 / 7 / 30 days (daily / weekly / monthly interval), ending at `visual.date`
  - otherwise → **SUM** of all values in the period, across **all sub-domains**,
    filtered by the visual's references when set
- **State badge** — first condition (by `order`) whose operator matches the current
  value decides color/icon; no match → grey "No Data" badge.
- **Chart data**:
  - line/bar/area → one series per `VisualReference` (or one series named after the
    visual when none); points = per-day totals **within the period only**
    (percentages: per-day moving-window values)
  - pie → sum per reference in the period (average for percentages); slice label from
    the matching reference's label, else the raw reference
  - gauge → current value per dataset; max = `max(target + tolerance)` across
    conditions, else value × 2, else 100
- **Caching** — aggregates cached 120s in the Django cache; the key includes the
  statistic's latest value timestamp, so new data invalidates naturally. Gauge max
  also keys on the conditions.

### Rendering

- `templates/.../render/visual.html` — two branches:
  - chart kinds: title, statistic name, period label, big number, state badge, ECharts
  - indicator: same header plus a large central circle (colored by condition) and a
    state pill. **The circle is transparent with no icon when there is no data / no
    matching condition — intended and fine.**
- The ECharts option is rendered server-side once (JSON in the page), then **polled**:
  a Glue function rebuilds the full option and the client calls
  `setOption(option, {notMerge: true})`.

| Surface | Cadence |
|---|---|
| Visual detail page | always (no flag); 3–5s per tick |
| `render_visual_region` slots | 10–12s per tick, only if `region.is_live_updated` |
| Signage kiosk display | 15–17s per tick, all sections of all slides |

No surface polls at a fixed period — each tick is `base + random(0–2s)`, so polls
drift apart. And visible data only changes when the 120s server-side cache expires or
new values land (cache keys include the latest value timestamp) — polling faster than
that mostly re-renders the same numbers.

The fast (3–5s) cadence exists only on the detail page, which shows exactly one
visual; multi-chart surfaces (region slots, kiosk) stay on the slower 10–12s /
15–17s cadences.

### Regions

`{% render_visual_region 'key' %}` renders the connected visual (or an "Unassigned"
card). Regions are connected/disconnected from the visual detail page
(`regions_card.html`); soft-deleting a visual detaches its regions
(`Visual.set_deleted`).

### Kiosk / signage

- Public display view at the signage key — **unauthenticated by design** (signage
  walls), `@xframe_options_exempt` for iframe embedding.
- Slides from linked presentations rotate on a timer (`slide_display_seconds`);
  arrow keys step manually.
- `kiosk-grid` CSS grid per slide; `html` font-size = `100vh / 50 × zoom` so everything
  (including ECharts fonts, via a patched `echarts.init`) scales with the screen.
  `?zoom=high|medium` (1.5 / 1.25), `?padding=`, and a fallback to zoom 1 on short
  screens.

## 2. Divergences & semantics to know

These match the code exactly — they are behaviors that surprise, not bugs:

- **Daily statistics → one-point line/area/bar charts.** The chart's time range equals
  the period, so a daily statistic shows exactly today. Example: "Site Sessions"
  (line, daily "Page Views") renders as a single dot at today's running total —
  intraday live-updates just move that dot up. There is no per-visual lookback.
- **"Current value" is a period total.** Weekly statistic = week-to-date sum; monthly =
  month-to-date sum. Not a rate. Example: "New Customers" (weekly, bar) on a Wednesday
  shows Mon+Tue+Wed in the big number, with one bar per day of that same week.
- **Percentages are moving-window averages**, not sums (2/7/30-day windows). Example:
  "Conversion Rate" (daily percentage) shows the average of today's and yesterday's
  daily rates, not today's raw rate — the badge evaluates the smoothed value.
- **Aggregation spans all sub-domains** — `statistic.values` has no sub-domain filter
  on the visual side. Example: the "Sales" domain has sub-domains "Leads",
  "Opportunities", and "Quotes". If "New Leads" values are recorded under both
  "Leads" (reference `web-form`) and "Opportunities" (reference `sales-call`), the
  "New Customers" visual sums both into one number and one chart. You cannot build a
  "web-form only" visual — the sub-domain dimension is invisible to visuals; references
  are the only slicing dimension, and two visuals on the same statistic always show the
  same merged total.
- **First matching condition wins** — `order` is precedence. Example: if "red if
  > 100" is ordered before "green if > 50", a value of 150 is red. The seed defaults
  (green `GT target` / yellow `BETWEEN target ± 10` / red `LT target`) are deliberately
  non-overlapping.
- **Gauge detail shows a raw number** — no unit, even for currency or percentage
  statistics; multiple references render multiple dials side by side sharing one max.
  Example: a gauge on "Revenue" (currency) with references `online` and `store`
  renders two dials both scaled 0→ceiling (ceiling = `max(target + tolerance)` across
  conditions), center text "12400" and "800" — no `$`, and the $800 dial reads as
  nearly empty on the shared scale. The seeded "Page Views per Minute" gauge has one
  reference, so the demo shows a single dial. → A1.
- **Duplication**: `VisualCondition.matches()` is implemented identically on the model
  and in `VisualConditionTransformationService` (drift risk). Production only calls the
  model method (via `current_condition`); the service copy is exercised by one test.
  → A3.
- **`period_range.html` compares raw interval strings** (`'monthly'`, `'daily'`) —
  works today, fragile (hardcoded choice values).

## 3. Kiosk performance deep-dive (low-powered targets)

Target hardware: smart TVs (Android TV, ~1–2 GB RAM, quad-core ARM) and Raspberry Pi
boxes running Chromium, displaying the page 24/7.

### Current cost profile

- **Every chart on every slide initializes at page load.** All slides are in the DOM
  (`x-show` = `display: none`), and Alpine `x-data` inits hidden elements too. With
  S slides × M sections there are S×M ECharts instances, each with its own canvas,
  `ResizeObserver`, and a `window` resize listener.
- **Every chart runs its own polling loop** (~15s + jitter): S×M independent
  `setTimeout` chains → ≈ 4 requests/min per chart. 5 slides × 4 sections ≈ 80
  req/min per wall, continuously.
- **Each poll is a full server-side rebuild**: `Visual.objects.get`, cache-key
  computation (a `Max(timestamp)` aggregate per key), and on cache miss (every ~120s
  per dataset) the full series aggregation queries; the response is the whole option
  JSON.
- **`setOption(notMerge: true)` every poll** forces a full re-layout even when the
  data didn't change — wasted CPU on weak hardware.
- **Hidden slides keep polling** with 0×0 canvases until their slide shows.
- **24/7 stability**: no page reload means JS heap drift from repeated
  setOption/canvas churn; GC pressure on a 1 GB TV over days.

### Mitigations (follow-up, not in this round)

- Initialize charts **lazily on first slide show**; destroy or pause hidden charts.
- Pause polling for non-visible slides (clear timer on hide, reschedule on show).
- **One shared poll loop** fanning out to visible charts, instead of N independent
  timers:
  - Today each chart div has its own Alpine `x-data` with its own `setTimeout` chain —
    S×M independent timers, each firing its own AJAX call.
  - Design: one page-level controller (Alpine on the kiosk-grid container) holds a
    single timer. Each chart registers itself on init (`{glueName, params,
    chartInstance, el}`). Each tick (~15s) the controller iterates only the **visible**
    charts and calls their Glue proxies in one `Promise.all` batch, applying each
    result.
  - Wins: no polling of hidden slides (the biggest one), one place to tune cadence and
    to pause on `document.hidden` (TV screens sleep), no per-chart timer drift, single
    code path.
  - Caveat: the request count per tick does not drop — Glue endpoints are per-function,
    so it is N_visible requests instead of N_total. Merging payloads would need a small
    batch view; not worth it at 5×4 chart scale.
- Consider a longer kiosk interval (30–60s) — the 120s server cache means faster polls
  rarely return new data.
- **Optional periodic full page reload** to reset the JS heap (a 24/7 page accumulates
  option/canvas churn; on a 1 GB TV that can mean days-to-sluggish-or-crash). **Done by
  the device layer, not the web app:**
  - smart TV: the kiosk app/launcher reload policy (Android TV kiosk mode) reloads the
    display URL every 30–60 min.
  - Raspberry Pi: a kiosk manager (small service or loop wrapping Chromium `--kiosk`)
    performs the reload.
  - In-page fallback: `setInterval(() => location.reload(), ...)` — zero infra, but
    reloads mid-slide (visible flash); mitigate by only reloading at slide 0, or by
    crossfading via a preloaded hidden iframe.
  - The reload is insurance, not a substitute for the lazy-init / pause-hidden fixes,
    which remove the churn at the source.
- (Considered `animation: false` for kiosk charts — **decided against it**; animations
  stay.)

## 4. Action items

### A1 — Gauge number/% alternation

The gauge's center detail alternates on a client-side timer (~5s) between:

- the value formatted by the statistic's value type (number / currency), and
- the percentage of the gauge ceiling (`value / max × 100`, 1 decimal).

Implementation: the gauge option carries an alternate-detail flag; `chart.html`'s
Alpine component runs the timer and toggles `series[0].detail.formatter` between
`'{value}'` and a client-side percent function (functions go through the JS API, not
the JSON payload). Note: for percentage-type statistics the two readings can look
similar (85 vs 85% of 100) — acceptable for v1.

### A2 — Documented, intentionally unchanged

- Transparent, icon-less indicator circle when there is no data — kept as-is.
- Public kiosk display URL — intentional (signage walls).
- Kiosk performance — mitigations listed in §3, deferred.
- First-condition-wins, period-total semantics, all-sub-domain aggregation —
  documented, unchanged.
- `animation: false` for kiosk charts — considered, not doing it.

### A3 — Deferred polish (small, separate)

- **Deduplicate `VisualCondition.matches()`**: production only calls the model method —
  `VisualTransformationService.current_condition` calls `condition.matches(value)`
  (transformation_service.py:149). The service-side copy
  (`VisualConditionTransformationService.matches`, transformation_service.py:353-369)
  is called by exactly one test (test_models.py:160). So: delete the service-side
  copy, point that one test at `condition.matches(...)`, and keep the model method as
  the single implementation (it sits next to `color`/`icon`, and the existing model
  tests target it). No behavior change; ~15 dead lines removed.

## 5. Key files

| Area | Path |
|---|---|
| Models | `django_spire/metric/visual/models.py` |
| Computation | `django_spire/metric/visual/services/transformation_service.py` |
| Charts | `django_spire/metric/visual/charts.py`, `django_spire/contrib/chart/charts.py` |
| Render template | `django_spire/metric/visual/templates/django_spire/metric/visual/render/visual.html` |
| Chart client | `django_spire/core/templates/django_spire/chart/chart.html` |
| Region tag | `django_spire/metric/templatetags/django_spire_metric_region.py` |
| Detail view | `django_spire/metric/visual/views/page_views.py` |
| Kiosk | `django_spire/metric/visual/signage/views/page_views.py`, `.../signage/page/display_page.html` |
| Interval math | `django_spire/metric/domain/statistic/interval.py`, `.../statistic/constants.py` |
| Value querysets | `django_spire/metric/domain/statistic/querysets.py` |
