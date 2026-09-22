# Metric Visual — Behavior Notes & Plan

Working notes on how `django_spire/metric/visual` behaves today, where
behavior diverges from expectation, and the planned changes.

## 1. How it works today

### Data model (`django_spire/metric/visual/models.py`)

- `Visual`
  - name, description, optional `Statistic` FK, `kind`
    (indicator | line | bar | area | pie | gauge)
  - `date` — evaluation date, defaults to today, **editable**
  - one proxy model + service per kind
    (`IndicatorVisual`, `LineChartVisual`, ...)
- `VisualCondition` — ordered rule
  - `state` (green/blue/yellow/grey/red)
  - `operator` (gt/gte/lt/lte/eq/between)
  - `target`, `tolerance`, `order`
- `VisualReference` — LIKE-style pattern (`%`/`_`) + label + order
  - selects which of the statistic's `reference` values become
    named datasets (series / pie slice / gauge)
- `VisualRegion` — unique slot key (e.g. `home:dashboard:hero`)
  - optional visual, `is_live_updated`, title
  - slot keys come from the
    `DJANGO_SPIRE_METRIC_VISUAL_REGIONS` setting

### Value computation (`services/transformation_service.py`)

Everything is anchored to `visual.date` (the "Evaluation Date"),
not necessarily now.

- **Period** = the statistic's interval around `visual.date`
  (`domain/statistic/interval.py`)
  - daily → that day, weekly → Mon–Sun, monthly → calendar month
- **Current value** (big header number)
  - no statistic / soft-deleted statistic → `0`
  - percentage statistics → moving-window **average of daily
    averages**, window = 2 / 7 / 30 days (daily / weekly / monthly
    interval), ending at `visual.date`
  - otherwise → **SUM** of all values in the period, across
    **all sub-domains**, filtered by the visual's references when
    set
- **State badge**
  - first condition (by `order`) matching the current value
    decides color/icon
  - no match → grey "No Data" badge
- **Chart data**
  - **line/bar/area** → one series per `VisualReference` (or one
    series named after the visual when none); points = per-day
    totals **within the period only** (percentages: per-day
    moving-window values)
  - **pie** → sum per reference in the period (average for
    percentages); slice label from the matching reference's label,
    else the raw reference
  - **gauge** → current value per dataset; max =
    `max(target + tolerance)` across conditions, else value × 2,
    else 100
- **Caching**
  - aggregates cached 120s in the Django cache
  - key includes the statistic's latest value timestamp → new
    data invalidates naturally
  - gauge max also keys on the conditions

### Rendering

- `templates/.../render/visual.html` — two branches:
  - **header** (both branches):
    - left: title (`display_title` or the visual's name) +
      statistic name (only if set)
    - right: period label + big number (both only if a statistic
      is set) + state badge (matched condition's color/icon, or
      grey dash when none)
  - **chart kinds**: ECharts below the header
  - **indicator**: same header plus a large central circle
    (colored by the matched condition; transparent with no icon
    when none) and a state pill
- Only the **chart** is live — everything else (header number,
  badge, attribute and card sections) is server-rendered once and
  static until page reload:
  - the ECharts option is rendered server-side once (JSON in the
    page)
  - then **polled**: a Glue function rebuilds the full option and
    the client calls `setOption(option, {notMerge: true})`

| Surface | Cadence |
|---|---|
| Visual detail page | always (no flag); 3–5s per tick |
| `render_visual_region` slots | 10–12s per tick, only if `region.is_live_updated` |
| Signage display page | 15–17s per tick, all sections of all slides |

- **Tick** = one poll cycle
  - timer fires → AJAX call to the chart's Glue function
  - server rebuilds the option → client re-renders the chart
  - takes one round-trip + re-render — usually milliseconds
    (longer when the server's 120s cache has expired)
- The figures above are the wait *between* ticks, not the duration
  of a tick.
- No surface polls at a fixed period — each tick is
  `base + random(0–2s)`, so polls drift apart.
  - why: charts that start together stop polling in sync (each
    re-rolls its offset independently every tick) → requests
    arrive staggered, not in bursts (thundering herd)
  - effect: spreads timing only — request volume is unchanged
- Visible data only changes when the 120s server-side cache
  expires or new values land (cache keys include the latest value
  timestamp) — polling faster than that mostly re-renders the same
  numbers.
- The fast (3–5s) cadence exists only on the detail page, which
  shows exactly one visual; multi-chart surfaces (region slots,
  signage display) stay on the slower 10–12s / 15–17s cadences.
- The intervals themselves are **hardcoded, not model columns**:
  - region: constant `VISUAL_REGION_LIVE_UPDATE_INTERVAL = 10`
    (`visual/constants.py:3`)
  - signage display: literal `15` in the `display_view` context
    (signage page_views.py:100)
  - the model columns that exist are on/off / rotation only:
    `VisualRegion.is_live_updated` (poll on/off) and
    `Signage.slide_display_seconds` (slide rotation, default 30s —
    not chart polling)

### Regions

- `{% render_visual_region 'key' %}` renders the connected visual
  (or an "Unassigned" card).
- Regions are connected/disconnected from the visual detail page
  (`regions_card.html`).
- Soft-deleting a visual detaches its regions
  (`Visual.set_deleted`).

### Signage display

- Public display view at the signage key
  - **unauthenticated by design** (signage walls)
  - `@xframe_options_exempt` for iframe embedding
- Slides from linked presentations
  - rotate on a timer (`slide_display_seconds`)
  - arrow keys step manually
- Scales to fit any screen
  - layout: `kiosk-grid` CSS grid per slide
  - `html` font-size = `100vh / 50 × zoom` → all rem-based sizes
    scale with screen height
  - ECharts fonts scale too — a patched `echarts.init` matches
    the root font size
  - query params: `?zoom=high|medium` (1.5 / 1.25), `?padding=`
  - fallback: short screens are forced to zoom 1

## 2. Divergences & semantics to know

These match the code exactly — they are behaviors that surprise,
not bugs:

- **Daily statistics → one-point line/area/bar charts.**
  - chart time range = the period → a daily statistic shows
    exactly today
  - example: "Site Sessions" (line, daily "Page Views") renders
    as a single dot at today's running total — intraday updates
    just move that dot up
  - there is no per-visual lookback
- **"Current value" is a period total.**
  - weekly = week-to-date sum; monthly = month-to-date sum — not
    a rate
  - example: "New Customers" (weekly, bar) on a Wednesday shows
    Mon+Tue+Wed in the big number, one bar per day of that same
    week
- **Percentages are moving-window averages**, not sums.
  - window = 2 / 7 / 30 days (daily / weekly / monthly interval)
  - example: "Conversion Rate" (daily percentage) shows the
    average of today's and yesterday's daily rates — the badge
    evaluates the smoothed value, not today's raw rate
  - only days that have data count — before any of today's values
    exist, the "2-day" value is just yesterday's rate
- **Sub-domains are invisible to visuals.**
  - a visual points only at a statistic (+ optional reference
    patterns); it never filters by sub-domain
  - writes are domain-safe: `record()` rejects a sub-domain from
    another domain (service.py:76-97)
  - **in practice** each statistic is fed by exactly one sub-domain
    (the click tracker uses a fixed statistic/sub-domain pair)
  - the one case nothing prevents: the *same* statistic recorded
    under two sub-domains of its own domain — e.g. "New Leads"
    under both "Leads" (`web-form`) and "Opportunities"
    (`sales-call`)
  - that is a valid write; a visual would silently sum both into
    one number and one chart
  - references are optional filters:
    - none set → whole statistic, one dataset named after the
      visual
    - set → each pattern becomes a narrowed, labeled dataset
- **First matching condition wins.**
  - `order` is precedence
  - example: "red if > 100" ordered before "green if > 50" → a
    value of 150 is red
  - seed defaults are deliberately non-overlapping: green
    `GT target` / yellow `BETWEEN target ± 10` / red `LT target`
- **Gauge detail shows a raw number.** → A1
  - no unit, even for currency or percentage statistics
  - multiple references → multiple dials side by side, sharing
    one max
  - example: "Revenue" (currency) gauge with references `online`
    and `store` → two dials scaled 0→ceiling (ceiling =
    `max(target + tolerance)` across conditions)
  - center text "12400" and "800" — no `$`; the $800 dial reads
    nearly empty on the shared scale
- **Duplication: `VisualCondition.matches()` is implemented
  twice.** → A3
  - identical logic on the model and in
    `VisualConditionTransformationService` (drift risk)
  - production only calls the model method (via
    `current_condition`)
  - the service copy is exercised by one test
- **`period_range.html` compares raw interval strings**
  (`'monthly'`, `'daily'`).
  - works today, fragile (hardcoded choice values)

## 3. Signage performance deep-dive (low-powered targets)

Target hardware: smart TVs (Android TV, ~1–2 GB RAM, quad-core
ARM) and Raspberry Pi boxes running Chromium, displaying the page
24/7.

### Current cost profile

- **Every chart on every slide initializes at page load.**
  - all slides are in the DOM (`x-show` = `display: none`), and
    Alpine `x-data` inits hidden elements too
  - S slides × M sections = S×M ECharts instances, each with its
    own canvas, `ResizeObserver`, and a `window` resize listener
- **Every chart runs its own polling loop** (~15s + jitter).
  - S×M independent `setTimeout` chains → ≈ 4 requests/min per
    chart
  - 5 slides × 4 sections ≈ 80 req/min per wall, continuously
- **Each poll is a full server-side rebuild.**
  - `Visual.objects.get` + cache-key computation (a
    `Max(timestamp)` aggregate per key)
  - cache miss (every ~120s per dataset) → the full series
    aggregation queries
  - the response is the whole option JSON
- **`setOption(notMerge: true)` every poll.**
  - forces a full re-layout even when the data didn't change —
    wasted CPU on weak hardware
- **Hidden slides keep polling.**
  - with 0×0 canvases until their slide shows
- **Memory is dominated by live canvases, not polling.**
  - one 1080p chart canvas ≈ 8 MB (×4 on a 4K panel at dpr 2)
  - 20 live charts ≈ 160 MB — the number that threatens a
    1–2 GB TV; independent of poll cadence
- **24/7 stability.**
  - no page reload → JS heap drift from repeated setOption/canvas
    churn
  - GC pressure on a 1 GB TV over days

### Mitigations (follow-up, not in this round)

1. **Lazily initialize charts**
   - init a chart when its slide is first shown
   - destroy or pause charts on hidden slides
2. **Pause polling for non-visible slides**
   - clear the timer on hide, reschedule on show
3. **One shared poll loop** (instead of N independent timers)
   - today: each chart div has its own Alpine `x-data` +
     `setTimeout` chain → S×M timers, S×M independent AJAX calls
   - design:
     - one page-level controller (Alpine on the kiosk-grid
       container) holds a single timer
     - each chart registers on init
       (`{glueName, params, chartInstance, el}`)
     - each tick (~15s): iterate only the **visible** charts,
       call their Glue proxies in one `Promise.all` batch,
       apply each result
   - wins:
     - no polling of hidden slides (the biggest one)
     - one place to tune cadence
     - one place to pause on `document.hidden` (TV screens sleep)
     - no per-chart timer drift
     - single code path
    - note: the request count itself is a small cost
      - ≈1–2 req/s per wall, a few KB/s
      - the real device cost is the `setOption(notMerge)`
        re-render each poll triggers
      - the visible-only loop above already minimizes that
4. **Longer poll interval (30–60s)**
   - the 120s server cache means faster polls rarely return
     new data

## 4. Action items

### A1 — Gauge value + reference

- **Layout (always):**
  - center = the value
  - bottom = the reference — ratio of the gauge ceiling
    (`value / max × 100`, 1 decimal)
- **Value-type rule:**
  - percentage type → show only the percentage
    (e.g. `12.34%`); no reference
  - number / currency type → formatted value
    (e.g. `$1,234.50`) + the reference at the bottom
- **How:**
  - the server pre-computes both strings per data item with the
    existing `format_statistic_value`
    (domain/statistic/format.py)
  - `chart.html` injects static formatters once at init (JS
    API — functions cannot travel in the JSON payload)

### A2 — Decided, intentionally unchanged

- **Transparent, icon-less indicator circle when there is no
  data** — kept as-is.
- **`animation: false` for signage charts** — considered, not
  doing it (animations stay).

### A3 — Deferred polish (small, separate)

- **Deduplicate `VisualCondition.matches()`.**
  - today:
    - production calls only the model method —
      `current_condition` → `condition.matches(value)`
      (transformation_service.py:149)
    - the service-side copy
      (`VisualConditionTransformationService.matches`,
      transformation_service.py:353-369) is called by exactly
      one test (test_models.py:160)
  - plan:
    - delete the service-side copy
    - point that one test at `condition.matches(...)`
    - keep the model method as the single implementation — it
      sits next to `color`/`icon`, and the existing model tests
      target it
  - outcome: no behavior change; ~15 dead lines removed

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
| Signage display | `django_spire/metric/visual/signage/views/page_views.py`, `.../signage/page/display_page.html` |
| Interval math | `django_spire/metric/domain/statistic/interval.py`, `.../statistic/constants.py` |
| Value querysets | `django_spire/metric/domain/statistic/querysets.py` |
