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
  - `target`, `tolerance` (half-width of the BETWEEN
    band — `|value − target| ≤ tolerance`; ignored by the
    other operators), `order`
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
  - daily → that day, weekly → Sun–Sat, monthly → calendar
    month
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
  - chart time range = the period → the chart shows exactly
    the evaluation day
  - a daily line/area renders as a single dot at that day's
    total — intraday updates just move that dot up
  - there is no per-visual lookback
- **"Current value" is the total over the full interval.**
  - weekly = the whole Sun–Sat; monthly = the whole month —
    not a rate
  - it equals week/month-to-date only while the days after the
    evaluation date have no data — later-dated values count too
  - example (a weekly statistic on live data): on a Wednesday
    the big number is Sun+Mon+Tue+Wed, one bar per day
- **Percentages are moving-window averages**, not sums.
  - window = 2 / 7 / 30 days (daily / weekly / monthly interval)
  - a daily percentage shows the average of that day's and the
    prior day's daily rates — the badge evaluates the smoothed
    value, not the raw rate
  - only days that have data count — before any of the day's
    values exist, the "2-day" value is just the prior day's rate
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
  - seed defaults: green `GT target` / yellow
    `BETWEEN target ± 10` / red `LT target` — the bands
    overlap on (target, target+10]; first-match order
    resolves it (above target → green, target−10..target
    → yellow, below → red)
- **Gauge detail shows a raw number.** → A2
  - no unit, even for currency or percentage statistics
  - multiple references → multiple dials side by side, sharing
    one max
  - example: "Revenue" (currency) gauge with references `online`
    and `store` → two dials scaled 0→ceiling (ceiling =
    `max(target + tolerance)` across conditions); center
    text "12400" and "800" — no `$`; the $800 dial reads
    nearly empty on the shared scale
- **Pie slices show the raw `reference` string when no
  reference pattern matches.** → A7
  - slices are the values grouped by
    `StatisticValue.reference` (querysets.py:137-149)
  - the pattern → label map comes from the visual's
    references; an unmatched reference falls back to the raw
    key (transformation_service.py:255-266)
  - the demo seed is exactly that case:
    - `VALUE_REFERENCES` seeds four **URL names** as the
      reference values (statistic/seeding/seeder.py:56-61)
    - seeded pie visuals get **no** references
      (visual/seeding/seeder.py:96-100) → empty label map →
      URL names in the slices and legend
  - the fallback is correct for real data (references are
    free-form — click tracking records actual view names,
    middleware.py:57); the demo data just collides with it
- **A fully drifted visual reads as a real zero.** → A5
  - references match nothing → `current_value` = 0
  - 0 satisfies the default `RED LT target` condition →
    the red badge (visual.html:24-29)
  - visually identical to a genuine zero; the cause is
    only visible by querying the values
- **Duplication: `VisualCondition.matches()` is implemented
  twice.** → A4
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

### Mitigations (batch B2 — ship with A1; see §4)

1. **Lazily initialize charts**
   - init a chart when its slide is first shown
   - destroy or pause charts on hidden slides
2. **Pause polling for non-visible slides** — subsumed by
   #3 (the shared loop already polls only visible charts);
   an optional stepping stone if #3 is deferred
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

Ordered by impact.

Batches:

| Batch | Contents | Why |
|---|---|---|
| B1 — display quick wins | A2, A3, A5 | low risk, independent, visible results; same render surface |
| B2 — signage + period semantics | §3 mitigations #1, #3, #4 + A1 | same rendering surface (charts.py + chart client); #1/#3/#4 cut live-chart count and re-renders |
| B3 — hygiene | A4 | zero behavior change |
| B4 — period offset | A6 | small, independent feature |
| — | A7 | decision record, no action |

### A1 — Chart period semantics (better drawings)

- the date + period pair gives charts two drawing assets
  that are unused today:
  - **anchor** — the evaluation date
  - **frame** — the full interval around it
- improvements:
  - **full frame, unelapsed part dimmed** (weekly / monthly)
    - today (non-percentage):
      - only days with data under the visual's reference
        patterns are drawn (GROUP BY day, querysets.py:126)
      - the range is the full interval (no clamping to
        visual.date, interval.py:19-22)
      - missing days vanish; the axis compresses to the
        data's extent
      - percentage charts instead draw a moving window
        ending at the date (§2)
    - monthly bar on Sep 18 → all 30 days drawn, days after
      the anchor ghosted → the chart shows why the number is
      month-to-date
    - weekly → always the full Sun–Sat frame (today it's a
      stub that grows through the week)
- tests: data-shape assertions (zero-fill, frame extent)
  in test_transformation_service.py; option assertions
  (ghost styling) in test_charts.py — both under
  visual/tests/test_services/
- deferred: previous-period comparison series (paired bars,
  previous-period line, pie delta suffix, gauge history) —
  the wall is a headline medium; re-add only if the need
  proves out
### A2 — Gauge: value, reference, scale

- **Layout (always):**
  - center = the value
  - bottom = the reference — ratio of the gauge ceiling
    (`value / max × 100`, 1 decimal)
- **Value-type rule (drives the label and the scale):**
  - percentage type → show only the percentage
    (e.g. `12.34%`); no reference; scale fixed 0–100
  - number / currency type → formatted value
    (e.g. `$1,234.50`) + the reference at the bottom
- **Scale fix (percentage → 100):**
  - today: `gauge_max` = max(target+tolerance) → value×2
    → 100 (transformation_service.py:300-320) — built for
    raw number scales
  - a 5% gauge with no conditions → max 10 → the needle
    sits dead center
  - fix: `if self._is_percentage(): return 100` — the
    helper already exists (transformation_service.py:86-90)
  - a percentage is 0–100 by definition; conditions then sit
    at meaningful positions (target 10 = the 10% position)
  - trade: a low rate (3–8%) sits near the bottom — honest
    over zoomed
- **How:**
  - the server pre-computes both strings per data item with
    the existing `format_statistic_value`
    (domain/statistic/format.py)
  - `chart.html` injects static formatters once at init (JS
    API — functions cannot travel in the JSON payload)
  - no-statistic gauge → empty data: the formatters must
    tolerate an empty / zero value
- tests: percentage gauge scale, with/without conditions

### A3 — Pie chart rendering

- **Options in `VisualPieChart.build_option_body`,
  charts.py:60-69:**
  - donut: `radius: ['45%', '70%']`, `center: ['50%', '45%']`
  - `label: {'show': False}` — drops the outside
    leader-line labels that collide with the card header
  - `legend: {'type': 'scroll', 'bottom': 0}` (today:
    `{'bottom': 30}`, contrib/chart/charts.py:21)
- tooltip stays the ECharts default — it already shows
  value + percent on hover (trigger 'item',
  contrib/chart/charts.py:112); an explicit formatter was
  considered, not doing it (cosmetic only)
- tests: option assertions in test_charts.py (donut
  radius, label hidden, legend scroll)

### A4 — Deferred polish (small, separate)

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
    - delete the method — it leaves
      `VisualConditionTransformationService` empty, so delete
      the class too
    - remove its import (service.py:26, one name from the
      3-name import block) and its attachment
      (`VisualConditionService`, service.py:81)
    - delete the wiring test (test_models.py:156-160) — its
      only purpose was asserting that attachment; the
      semantic tests already target `condition.matches(...)`
    - keep the model method as the single implementation — it
      sits next to `color`/`icon`, and the existing model tests
      target it
  - blast radius: exactly 4 spots (class, import, attachment,
    test) — a repo-wide grep found nothing else referencing
    the service copy
  - outcome: no behavior change; ~24 lines removed

### A5 — "No matching data" vs a true zero

- today: a drifted reference (matches nothing) → value 0 →
  the red `LT target` badge — indistinguishable from a real
  zero
- add a render flag — references set AND
  `for_reference_patterns(patterns).count() == 0` AND the
  statistic has values → `no_matching_data`
- render the existing no-condition state (A7's transparent
  circle) + a "no matching data" caption, instead of 0 + red
- both call sites: `render_context()`
  (transformation_service.py:332-346) and the detail view's
  `_visual_context` (page_views.py:23-37)
- the unfiltered-has-values check keeps a brand-new
  statistic (no data at all) on the existing no-data path
- the all-time count is deliberate: a rename with legacy
  rows still inside the 90-day retention keeps the count > 0, 
  so the flag fires only after they prune out
- tests:
  - flag fires: references set, zero matches, statistic
    has values
  - flag stays off: empty statistic (existing no-data
    path), no references, or any match exists
  - the caption renders in visual.html

### A6 — Period offset selector (detail page)

- today: viewing a past period means editing + saving
  `visual.date` — a persisted change that shifts every
  surface (cards, detail, signage) until it's edited back
- add a display-only shift on the detail page: a native
  select (This/Last month, This/Last week, Yesterday) →
  `?period_offset=N`; no JS — a full reload per choice
- a ~15-line helper next to `interval_range`
  (interval.py:14): daily −N days, weekly −7N days, monthly
  −N months, day-clamped (Jan 31 → Dec 31)
- the shifted date threads through existing paths —
  `current_value(value_date=...)` and
  `date_range(value_date=...)` already take it; the chart
  needs it in `params` (charts.py:33-57, `series_datasets`)
- nothing saved: cards, regions, signage keep the persisted
  date (`render_context` unchanged)
- not A1's comparison series — renders period N−1 only
- the period attribute and header show the shifted range —
  the existing raw-range rendering follows the shifted
  date
- when A1 ships, its ghost frame follows the shifted date,
  not the saved one

### A7 — Decided, intentionally unchanged

- **Transparent, icon-less indicator circle when there is no
  data** — kept as-is.
- **`animation: false` for signage charts** — considered, not
  doing it (animations stay).
- **Pie slice labels falling back to raw `reference` strings
  when no reference pattern matches** (current data shows
  raw keys) — out of scope.
- **Daily one-point line/area/bar charts** — kept as-is (no
  trailing window; a weekly visual provides the trend view).
- **Anchor marker (a `markLine` at the evaluation date)** —
  considered, not doing it (the ghosted unelapsed part
  already shows where the frame ends).
- **Unifying Evaluation Date + Period display**
  (`period_label`) — considered, not doing it (both card
  attributes stay as-is; the date formats remain mixed).
- **Per-reference match counts on the detail page** —
  considered, not doing it (an all-time total is a weak
  signal: the charts already show the per-reference daily
  spread; the save-time block + the no-match state cover
  the important cases)

## 5. Files to change

| Area | Path | Items |
|---|---|---|
| Computation | `django_spire/metric/visual/services/transformation_service.py` | A1, A2, A4, A5, A6 |
| Visual services | `django_spire/metric/visual/services/service.py` | A4 |
| Charts | `django_spire/metric/visual/charts.py` | A1, A2, A3, A6 |
| Interval math | `django_spire/metric/domain/statistic/interval.py` | A6 |
| Detail view | `django_spire/metric/visual/views/page_views.py` | A5, A6 |
| Render template | `.../visual/render/visual.html` | A5 |
| Detail page | `.../visual/page/detail_page.html` | A6 |
| Chart client | `django_spire/core/templates/django_spire/chart/chart.html` | A2, §3 #1/#3 |
| Signage display | `django_spire/metric/visual/signage/views/page_views.py` | §3 #4 |
| Signage page | `.../signage/page/display_page.html` | §3 #1/#3 |
| Tests | `django_spire/metric/visual/tests/` (services, views, models), `.../signage/tests/`, `.../domain/statistic/tests/test_interval.py` | all |

Template paths are under `django_spire/metric/visual/templates/django_spire/`.
