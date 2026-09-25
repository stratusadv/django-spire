# Metric Visual — Behavior Notes & Plan

Working notes on how `django_spire/metric/visual` behaves today, the
target display behavior, where behavior diverges from expectation,
and the planned changes.

## 0. Target behavior

The visual app displays statistics the way a person reading a wall or
daashboard expects: the current unit's value, plus a lookback of the
recent units, anchored to today and never going stale.

- **Always current.** A visual has no date of its own. Every surface
  (detail page, region slots, signage walls) renders the unit
  containing today; the `Visual.date` column is removed (A7).
- **Unit-based lookback.** A chart shows the N most recent units of
  the statistic's interval, ending with the unit containing the
  display date:
  - daily → 8 days (today + the preceding 7)
  - weekly → 12 weeks (this Sun–Sat week + the preceding 11)
  - monthly → 13 months (this month + the preceding 12)
  - N is a per-visual choice (`display_unit_count`); unset = the
    interval default (A1)
- **Header** = the current unit's value (today / week-to-date /
  month-to-date), labeled with the display range the chart covers
  (A1)
- **All series share the frame** — one series per reference, each its
  own color, all over the same unit range (A1)
- **Browsing a past date** stays display-only: `?value_date=...`, the
  window ends at the unit containing the picked date, nothing is
  saved (A6)

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
not necessarily now — saved once at creation; nothing
rolls it forward.

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

### Value retention (`domain/statistic`)

- each recorded event is a new `StatisticValue` row
  (`StatisticProcessorService.add_value`,
  processor_service.py:57-62) — rows accumulate, never
  auto-deleted on write
- two cleanup mechanisms exist, both only via the
  `prune_metric_statistic_values` management command:
  - age: delete rows older than
    `DJANGO_SPIRE_METRIC_RETENTION_DAYS` (default 90)
  - cap: per (statistic, sub-domain, reference), keep the
    latest `DJANGO_SPIRE_METRIC_TRACKING_VALUES_MAX`
    (default 1000) rows
- nothing in the repo schedules the command (no Celery
  beat, no call from the tracking path) — expected to be
  scheduled in the future (ops/cron); until then rows
  persist indefinitely

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
  - **A9 correction (misdiagnosis retracted)**: an earlier
    revision of this plan claimed the `{'kwargs': ...}` wrap in
    chart.html:49 broke every poll. It did not —
    `FunctionGlue.execute(self, kwargs)` has its own `kwargs`
    parameter that consumes the wrapper key before
    `function(**kwargs)` unpacks the *inner* dict, so the
    original wrap was always correct and polls worked. The B2
    implementation briefly applied a flat call instead, which
    genuinely broke every poll (`ValueError: missing required
    argument: 'kwargs'`); it has been reverted and the
    convention is now pinned by an endpoint-level test (see
    A9 and the implementation log)

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
  reference pattern matches.** → A8
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
  - the polls return live data (the A9 "broken poll" claim was
    a misdiagnosis — see the A9 item); the re-render cost below
    is what lands
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

Numbered by workstream, not ranked by impact — A1+A7 (walls stop
going stale and show the unit lookback) and A5 (no false red
zeros) carry the most behavior change; the batch table is the
execution order.

Batches:

| Batch | Contents | Why |
|---|---|---|
| B1 — display quick wins | A2, A3, A5 | low risk, independent, visible results; same render surface |
| B2 — core display change | A1 + A7 + A6 + A9 | one model migration (drop `date`, add `display_unit_count`), one computation core, one render surface — the window, always-today, and browse are interlocked; A6's chart params ride the existing poll plumbing, whose call convention A9 re-verified and pinned with a test |
| B3 — signage performance | §3 mitigations #1, #3, #4 | client-side JS architecture, independent of the data shape; split out to keep B2's diff small |
| B4 — hygiene | A4 | zero behavior change |
| — | A8 | decision record, no action |

### A1 — Unit-based display window (the core change)

- **What it replaces.** Today a chart is drawn over the
  statistic's interval around the saved date (1 day / Sun–Sat /
  calendar month), only days with data, axis compressed to the
  data's extent; a daily statistic renders as one point. The
  earlier "ghost the unelapsed part of the frame" plan is
dropped — under the window design every unit in the frame is
complete except the current one, and the current one is shown
as-is (its partial accumulation matches the header number). The
earlier deferred "previous-period comparison series" is what the
window delivers: today's unit plus the preceding units in one
frame, on every surface.
- **Model** — new field `Visual.display_unit_count`
  - `models.PositiveSmallIntegerField(null=True, blank=True)`,
    form-validated 1..104
  - unset → interval default: daily 8, weekly 12, monthly 13
    (constants in `visual/constants.py`)
  - exposed in the form ("Display units" label + hint explaining
    the default); detail card gets a "Display units" attribute
    (effective count + interval word, e.g. "12 week(s)"), hidden
    when no statistic is set
  - same migration as the `date` removal (A7)
- **Frame** — `display_window_range(interval, end_date, count)` in
  `domain/statistic/interval.py`
  - N consecutive units ending at the unit containing `end_date`
    (= today, or A6's picked date)
  - daily: `end_date − 7 .. end_date` (default 8)
  - weekly: the Sunday of the week containing `end_date`, minus
    count−1 weeks, through that week's Saturday (default 12)
  - monthly: the 1st of the month count−1 months before
    `end_date`'s month, through the last day of `end_date`'s
    month (default 13)
- **Chart points** — per unit, per reference
  - non-percentage → SUM of the unit's values
  - percentage → the unit's raw average (no moving window — the
    smoothed series is retired; the header's moving-window
    `current_value` is unchanged)
  - empty units → 0 (stable 8/12/13-point axis)
  - unit label = the unit's start date (day / Sunday / 1st of
    month)
  - new `StatisticValueQuerySet.unit_points(interval, start, end)`
    generalizing the then-existing `series_points` (since deleted
    as dead code): daily = TruncDate as-is, weekly = week start
    (Sun), monthly = month start
  - bucketing stays DB-portable: fetch day-level totals for the
    window (bounded: ≤ 13 months ≈ 395 days) and aggregate days
    into units in Python — a SQL week-start expression differs
    between Postgres and SQLite, and the project supports both
- **Header** — `current_value` semantics unchanged (today /
  week-to-date / month-to-date); the small label under the
  number and the detail card's Period attribute show the window
  range instead of the single interval period; the Evaluation
  Date attribute is removed (A7)
- **Context keys** — `period_start`/`period_end` keep their
  names; only their meaning changes (single interval period →
  window range). Two producers set them, seven consumers pass
  them through (no consumer edits needed):
  - producers: `render_context()`
    (transformation_service.py:337-345) and the detail view
    (`_visual_context` page_views.py:28-29, `detail_view` :82)
  - consumers: `render/period_range.html`,
    `render/region_visual.html`, `card/detail_card.html:28,69`,
    `signage/page/display_page.html:194`,
    `presentation/render/slide.html:31`,
    `presentation/card/section_card.html:33`, the
    `render_visual_region` templatetag
    (templatetags/django_spire_metric_region.py:54-55)
  - `period_range.html`'s monthly branch prints only the month
    name (`{{ period_start|date:'F' }}`) — a 13-month window
    needs a start–end range there
- **Pie** — sum per reference over the whole window (percentage:
  average); `series_breakdown` already takes start/end — pass the
  window range
- **Gauge** — unchanged (current unit's value per dataset; A2's
  format/scale fix still applies)
- **Seeder** — `VisualSeeder._seed_visual_values` stamps its
  30-point wave inside `date_range()` (visual/seeding/ seeder.
  py:125) — the single interval around the saved date. After A7
  that is one day for a daily statistic and the demo wave
  collapses into one point; seed the wave across
  `display_window_range(...)` instead. (The domain seeder's
  30-day values still fill the window, but the wave shape is
  what the demo charts are built from)
- **Caching** — the effective unit count joins the
  `_cache_key` parts
- **Tests** — frame extent per interval, count override,
  zero-fill, weekly/monthly bucketing, percentage raw average,
  window range at A6's picked date; option assertions (point
  count per kind) in test_charts.py; seeder wave spans the
  window — under visual/tests/test_services/. Update existing
  assertions written for the old behavior:
  test_transformation_service.py:517 (`period_start ==
  period_end` — a daily window is 8 days now) and the
  `visual.date = ...` fixtures (A7)
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

- **Options in `VisualPieChart`** (charts.py):
  - stays a **pie, not a donut** — user decision, no
    `radius` change (filled pie, ECharts default size)
  - `center: ['50%', '45%']` on the series — nudged slightly
    up so the pie clears the bottom legend
  - `label: {'show': True}` — slice labels stay shown
    (the original plan hid them to avoid card-header
    collision; the decision was reversed to try them
    visible)
  - `default_legend = {'bottom': 0, 'left': 'center',
    'width': '90%'}` on `VisualPieChart` (today:
    `{'bottom': 30}`, contrib/chart/charts.py:21) — a plain
    legend that wraps lines within 90% width: every
    reference stays visible, no paging. Overrides
    `default_legend` (not `legend`) so the base `bottom: 30`
    default does not leak through the `{**default, **legend}`
    merge — same pattern as `PieChart.default_tooltip`.
    Considered and rejected in the browser: a bottom scroll
    legend (`type: 'scroll'` never pages without an explicit
    width — an auto-width one lays items at natural size —
    and its paging arrows proved hard to discover) and a
    vertical right-edge column (long slug labels make the
    column wide)
- tooltip stays the ECharts default — it already shows
  value + percent on hover (trigger 'item',
  contrib/chart/charts.py:112); an explicit formatter was
  considered, not doing it (cosmetic only)
- the pie stays data-shape tested (slices/labels); the new
  option keys (label shown, center, legend) are deliberately
  not pinned — cosmetic layout, verified visually

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
- the form guard (forms.py:114-130) blocks saving a dead
  pattern while the statistic has values, so this state
  only arises via:
  1. a pattern typed ahead of an empty statistic (no
     suggestions, check skipped) where the data later
     arrives under a different name
  2. the recorder renaming references after the fact
     (view rename; the `ds:` → `django_spire:` namespace
     change happened in this deployment)
  3. the recorder stopping a reference and its rows being
     deleted by a scheduled prune (not yet scheduled —
     §1 "Value retention")
  4. writes outside the form (shell/DB/API)
- add a `no_matching_data` flag to the render context —
  true only when all three hold:
  1. the visual has references set
  2. those patterns match zero values (all-time) —
     `statistic.values.for_reference_patterns(patterns).count() == 0`
  3. the statistic has values at all (unfiltered)
- render the existing no-condition state + a "no
  matching data" caption, instead of 0 + red
  - indicator: the transparent circle (A8) + caption
  - chart kinds: grey badge + caption (charts already
    empty — no matching points / slices)
- both call sites: `render_context()`
  (transformation_service.py:332-346) and the detail view's
  `_visual_context` (page_views.py:23-37)
- the unfiltered-has-values check keeps a brand-new
  statistic (no data at all) on the existing no-data path
- the all-time count is deliberate: a rename with legacy
  rows keeps the count > 0, so the flag fires only after
  those rows are deleted — which needs
  `prune_metric_statistic_values` scheduled (not yet —
  §1 "Value retention")
- rationale: the wall's audience is non-technical, so a
  false red 0 stays unexplained until a technical person
  investigates; the caption makes the cause self-evident
  and removes that dependency
- tests:
  - flag fires: references set, zero matches, statistic
    has values
  - flag stays off: empty statistic (existing no-data
    path), no references, or any match exists
  - the caption renders in visual.html

### A6 — Date-jump period browse (detail page)

- A7 removes the saved date, so a display-only browse is the
  only way to view a past period
- this makes it display-only, on the detail page only
  - for inspection — "what did last week look like?"
  - one URL parameter: `?value_date=YYYY-MM-DD`
  - zero JS — a plain form submit
  - nothing is saved: no parameter renders today,
    exactly as the default
  - `render_context` unchanged — cards, regions, and
    signage are untouched
  - the wall deliberately gets no jump
    - it is always current (A7) — a transient URL date
      on a fixed kiosk URL is easy to forget
- a date-jump form — one native date input + Go
  - below the Period attribute (detail_card.html:66-71)
  - `max` = today — no future dates (they have no data)
    - the view re-checks, since `max` is only a UI hint
  - renders the display window (A1's unit count) ending at the
    unit containing the picked date
  - clearing the input + Go returns to today
  - shown only when a statistic is set
- threading
  - the server-side data methods are ready: all five take
    `value_date` (transformation_service.py:76, 114, 191, 234,
    270)
  - the view passes the shifted date to `current_value()` /
    `current_condition()` (page_views.py:26-27) so the header
    number and badge match the shifted window, and to both
    `date_range()` calls in the detail path
    (`_visual_context` :28-29, `detail_view` :82)
  - **charts are the non-free part** (poll call convention
    re-verified in A9):
    - the view puts `value_date` into the chart instance's
      params (`transformation.chart(params={'visual_pk': ..., 'value_date': ...})`) so the initial render (`to_option_dict`) and every poll carry it
    - the five chart bodies (charts.py:30-95) forward
      `value_date` from `params` — pie and gauge included
    - `value_date` arrives from the client JSON as a
      `YYYY-MM-DD` string; the chart bodies parse it to a
      `date` before calling the transformation methods (they
      do `timedelta` math and `.isoformat()` on it)
- the Period attribute + header label follow automatically
  - both render from the `period_start`/`period_end` context
    (detail_card.html:69, period_range.html:1-7) — now the
    window range, self-evident even for a picked past date
- the Evaluation Date attribute is removed (A7); with a picked
  date active, the window range in the Period attribute shows
  where the data comes from
- renders one window (A1) ending at the picked date — no other
  period shown alongside
- extension to signage (out of scope)
  - `?value_date=YYYY-MM-DD` on the display URL
  - `display_view` → `display_slides()`
    (signage/services/transformation_service.py:46) →
    each section's `render_context(value_date=...)` (:63)
  - the operator navigates the kiosk to the URL to
    preview and back to the plain URL to revert
- tests:
  - the form renders the window ending at the picked date
  - missing or invalid param renders today
  - detail view context shifted
    (value, condition, period, chart params)

### A7 — Always-today date (drop the date)

- today: `date` defaults to `timezone.localdate` once at
  creation (models.py:56)
  - every computation keys to the saved value
    (transformation_service.py:77, 128)
  - nothing rolls it forward
  - a daily visual on a wall shows creation-day's number
    forever
- decision: a presented visual is always the current data for
  its statistic's interval — no date field, no pinning, no
  follow-today checkbox. The earlier `date_follows_today`
  flag plan is dropped; the column is removed instead.
- **Model**
  - drop `Visual.date` (same migration adds
    `display_unit_count`, A1)
  - drop the form field (forms.py:48, 50) and the form
    template line (form/form.html:31)
  - drop the detail card's Evaluation Date attribute
    (detail_card.html:61-64)
  - drop `date` from admin `list_display` (admin.py:29)
- **Anchor** — every `value_date or self.obj.date` fallback
  becomes `value_date or timezone.localdate()`
  - five sites: transformation_service.py:52, 77, 128, 203,
    282
  - the first is the cache-key site — missing it would let a
    rolled day reuse yesterday's key and serve the stale
    aggregate
- every surface rolls at midnight
  - cards, regions, signage, and detail
  - the 120s cache absorbs the rollover lag
- A6 is the only path to a non-today date, and it is
  display-only (nothing is saved)
- tests:
  - a daily visual recomputes for the new day (shift the
    test clock across midnight)
  - the cache key changes with the date
  - fixtures that set `date` drop the kwarg or pass
    `value_date` instead

### A8 — Decided, intentionally unchanged

- **Transparent, icon-less indicator circle when there is no
  data** — kept as-is.
- **`animation: false` for signage charts** — considered, not
  doing it (animations stay).
- **Pie slice labels falling back to raw `reference` strings
  when no reference pattern matches** (current data shows
  raw keys) — out of scope.
- **Daily one-point line/area/bar charts** — replaced: A1's
  window draws 8 daily points.
- **Ghosting the current in-progress unit** (a half bar /
  dimmed point to signal the week/month is still
  accumulating) — considered, not doing it (the header number
  plus the window range make the to-date status legible; the
  partial unit matches the header).
- **Anchor marker (a `markLine` at the display date)** —
  considered, not doing it (the frame ends at the display date
  by construction).
- **Moving-window smoothing on percentage chart points** —
  replaced by the raw per-unit average (A1); the header keeps
  the moving-window value, so the number and the latest point
  can differ slightly by design.
- **The "Evaluation Date" card attribute** — removed (A7); the
  Period attribute shows the display range (A1).
- **Per-reference match counts on the detail page** —
  considered, not doing it (an all-time total is a weak
  signal: the charts already show the per-reference unit
  spread; the save-time block + the no-match state cover the
  important cases).
- **Renaming `period_start`/`period_end` to
  `display_start`/`display_end`** — considered, not doing it
  (seven templates/templatag/view sites pass the keys through;
  reusing the names keeps the A1 diff to the two producers).
- **The chart poll call convention as part of A1/A6** — it is
  its own item (A9): not a pre-existing bug (the original wrap
  was correct), but re-verified with an endpoint-level test,
  because A6's live browsed charts depend on the poll carrying
  `value_date` intact.

### A9 — Chart live-update call convention (re-verified, not a bug)

- **The "broken poll" premise of this item was a misdiagnosis.**
  - an earlier revision claimed the client's
    `proxy.execute({'kwargs': this._params || {}})`
    (core/.../chart/chart.html:49) failed server-side with
    `TypeError: missing 'visual_pk'`
  - that trace was wrong: `FunctionGlue.execute(self, kwargs)`
    (`django_glue/glue/function.py:60`) has a single required
    parameter named `kwargs`; the callable-attribute resolver
    (`django_glue/glue/attributes/callable.py`) maps the
    client's top-level call-kwargs onto that parameter, and
    `execute` then runs `function(**kwargs)` — unpacking the
    *inner* dict into `_build_option(visual_pk=...,
    value_date=...)`. The original wrap was always the correct
    convention, and the polls worked
- **What actually happened in B2** — the flat call
  `proxy.execute(this._params || {})` was applied as "the A9
  fix", which made every poll of every Glue-polled chart (5
  visual + 2 home demo) raise `ValueError: Attribute 'execute'
  missing required argument: 'kwargs'. Provided: ['visual_pk']`
  (500 per tick, silent in the UI). Reverted to the original
  wrap.
- **Why tests never caught it** — the suite calls the data
  functions directly (`visual_line_chart_data(visual_pk=...)`),
  never through the
  `/__dg__/callable_attribute/<name>/execute/` endpoint.
  Added an endpoint-level test (wrapping
  `knowledge/collection/tests/test_views/test_form_views.py`'s
  `_call_glue_attribute` pattern): the wrapped shape returns
  the rebuilt option.
- **Convention note** — the client's `_filterKwargs` passes
  the wrapped `kwargs` key through unfiltered only because
  every glued chart data function is the base
  `Chart._build_option(cls, **kwargs)` (zero declared params,
  so the identity's `params` list is empty). A data function
  with explicit declared params would get its call filtered to
  `{}` and fail; if such a chart is ever added, the poll
  convention must be re-checked.
- **Scope** — the Glue-polled data functions in the repo are
  the five visual chart bodies **plus two demo charts** on the
  home page (`monthly_sales_chart`, `productivity_area_chart` —
  `test_project/app/home/charts.py`, included via `chart.html`
  from `home/page/chart_demo_page.html`). All are `Chart`
  subclasses, so the poll path is `_build_option(**kwargs)` →
  `build_option_body(**kwargs)` for every caller; the demo
  charts poll with empty params.
- **Tests**
  - endpoint: the wrapped call returns the rebuilt option (200)
  - unit: `visual_line_chart_data(visual_pk=pk)` returns the
    option (and, with `value_date` as a string, A6's shape)

## 5. Files to change

| Area | Path | Items |
|---|---|---|
| Computation | `django_spire/metric/visual/services/transformation_service.py` | A1, A2, A4, A5, A6, A7 |
| Interval | `django_spire/metric/domain/statistic/interval.py` | A1 |
| Value querysets | `django_spire/metric/domain/statistic/querysets.py` | A1 |
| Visual model | `django_spire/metric/visual/models.py` | A1, A7 |
| Migration (new) | `django_spire/metric/visual/migrations/` | A1, A7 |
| Visual form | `django_spire/metric/visual/forms.py` | A1, A7 |
| Visual constants | `django_spire/metric/visual/constants.py` | A1 |
| Visual services | `django_spire/metric/visual/services/service.py` | A4 |
| Charts | `django_spire/metric/visual/charts.py` | A1, A2, A3, A6 |
| Detail view | `django_spire/metric/visual/views/page_views.py` | A5, A6 |
| Visual admin | `django_spire/metric/visual/admin.py` | A7 |
| Visual seeder | `django_spire/metric/visual/seeding/seeder.py` | A1 |
| Render templates | `.../visual/render/visual.html`, `.../render/period_range.html`, `.../visual/form/form.html` | A1, A5, A7 |
| Detail card | `.../visual/card/detail_card.html` | A1, A6, A7 |
| Chart client | `django_spire/core/templates/django_spire/chart/chart.html` | A2, A9, §3 #1/#3 |
| Signage display | `django_spire/metric/visual/signage/views/page_views.py` | §3 #4 |
| Signage page | `.../signage/page/display_page.html` | §3 #1/#3 |
| Tests | `django_spire/metric/visual/tests/` (services, views, models, seeder), `.../signage/tests/` | all |

Template paths are under `django_spire/metric/visual/templates/django_spire/`.

## 6. Implementation log

### A1 — done

- **Model** — `Visual.display_unit_count`
  (`PositiveSmallIntegerField(null=True, blank=True)`, verbose_name
  "Display units"), migration `0008_visual_display_unit_count`.
  Form field validates 1..104
  (`DISPLAY_UNIT_COUNT_MIN/MAX` in `visual/constants.py`); unset →
  `DEFAULT_DISPLAY_UNIT_COUNTS` (daily 8 / weekly 12 / monthly 13) via
  `effective_display_unit_count()`. The declared form field carries
  an explicit `label` (declared fields don't inherit the model
  verbose_name, so django-glue's metadata resolver otherwise yields
  a blank label) and `help_text` — `widget.html` renders it as the
  hint automatically. Detail card shows a "Display Units"
  attribute via `display_unit_label()` (e.g. "12 week(s)",
  `DISPLAY_UNIT_LABELS` in constants), hidden when no statistic is
  set.
- **Frame** — `display_window_range(interval, end_date, count)` +
  `unit_end` / `next_unit_start` in `domain/statistic/interval.py`
  (pure date math, DB-agnostic).
- **Chart points** — `StatisticValueQuerySet.unit_points(interval,
  start, end, *, average)` : one query for day-level
  `Sum` + `Count`, days bucketed into units in Python (Postgres/
  SQLite portable), empty units zero-filled, point label = unit
  start. Percentages use the unit's raw `Avg` (moving-window series
  retired — `_percentage_series` deleted; `current_value` header
  keeps its moving-window value).
- **Service** — `display_window(value_date)` /
  `display_unit_count()` on the transformation service;
  `series_datasets` points and `series_breakdown` (pie) now span the
  window; `render_context()` and the detail view's
  `period_start`/`period_end` are the window range (context key
  names unchanged — all seven consumers untouched); the effective
  unit count joins the `_cache_key` parts. `date_range()` remains
  for the header's current-unit value only.
- **Label** — `period_range.html` now prints a start–end range for
  any multi-unit window (single date when start == end).
- **Seeder** — `_seed_visual_values` stamps its 30-point wave
  across `display_window()` instead of the single interval.
- **Tests** — 527 passed (was 512: +15). New: window-frame extents
  per interval + counts (domain `test_interval.py`), service window
  frames / count override / no-statistic fallback, count-driven
  series length, monthly bucketing, raw unit average for
  percentages (two values in one day → their mean). Updated:
  series assertions to 8/12/13-point zero-filled windows,
  `render_context` period = 8-day window, A6 picked-date period =
  12-week window ending at the picked week.
- **Deviation** — the "Evaluation Date attribute removed" line was
  already satisfied by A7; no other deviations.

### A4 + A7 + A6 (+ A9 client convention) — done

- **A4** — deleted `VisualConditionTransformationService` (and its
  `VisualConditionOperatorChoices` import), the import + attachment in
  `services/service.py`, and the wiring test in `test_models.py`.
  `VisualCondition.matches` on the model is the single implementation.
- **A7** — dropped `Visual.date` (model + migration
  `0007_remove_visual_date`), all five `value_date or self.obj.date`
  anchors now fall back to `timezone.localdate()` (including the
  cache-key site), form field + template line + admin `list_display`
  entry + detail-card "Evaluation Date" attribute removed. Tests that
  pinned `visual.date = date(2026, 5, 15)` now pass the date
  explicitly (`value_date=` or via chart params); new tests cover the
  always-today anchor, midnight rollover (patched `timezone.localdate`),
  and the cache key changing with the date.
- **A6** — detail page only: `?value_date=YYYY-MM-DD` parsed in
  `_browse_value_date` (invalid or future → ignored → today), threaded
  through `current_value` / `current_condition` / `date_range` and into
  the chart's Glue params (`transformation.chart(value_date=...)` →
  `params['value_date']` as `YYYY-MM-DD`). The five chart bodies parse
  the string via `_value_date()` and forward it to
  `series_datasets` / `series_breakdown` / `dataset_values`. Plain GET
  form (native date input, `max` = today, Go) under the Period
  attribute in `detail_card.html`, rendered only when a statistic is
  set; clearing the input returns to today. `render_context()` is
  untouched — regions, signage, and presentations stay always-today.
  The browsed window is the A1 display window (per-visual unit
  count) ending at the unit containing the picked date.
- **A9 (client convention)** — the original
  `proxy.execute({'kwargs': this._params || {}})` in `chart.html:49`
  was **always correct** and this "fix" was a misdiagnosis:
  `FunctionGlue.execute(self, kwargs)` has its own `kwargs` parameter
  that the attribute-call resolver maps the client's top-level
  call-kwargs onto, and `execute` then does `function(**kwargs)` —
  unpacking the *inner* dict. A B2 change to a flat call
  (`proxy.execute(this._params || {})`) was the actual regression:
  every poll of all 7 Glue-polled charts (5 visual + 2 home demo)
  500'd with `ValueError: Attribute 'execute' missing required
  argument: 'kwargs'. Provided: ['visual_pk']`. Reverted to the
  original wrap. A6's chart threading is unaffected — `value_date`
  rides inside the wrapped params either way.
- **Tests** — metric suite 512 passed (was 502: +11, −1); core +
  home smoke 359 passed. New: `value_date` string shape, localdate
  anchor through the chart path, and six detail-view A6 cases
  (picked period, missing/invalid/future param, form rendered /
  hidden). (The original "flat-kwargs acceptance for all five data
  functions" loop was later deleted — tautological, and named after
  the retracted flat convention; the bar body it alone exercised now
  has a dedicated `test_bar_chart_option`.)
- **A9 follow-up (regression pin)** — added endpoint-level tests in
  `test_page_views.py::VisualChartExecuteTestCase` that POST through
  the real `/__dg__/callable_attribute/visual_line_chart/execute/`
  route (the suite had only ever called the data functions
  directly, so the flat-call regression shipped green): the wrapped
  shape returns the rebuilt option (200). Also pins the template
  line in `test_detail_view_with_chart_kind`. Metric suite re-run
  after the revert is green.
- **Detail-card chart include (explicitness only)** —
  `detail_card.html`'s include of `render/visual.html` did not
  pass `chart` in its `with` clause, while the other three
  includers (region, signage, presentation) do. Added
  `chart=chart` for parity — a behavior no-op, because an include
  without `only` inherits the full parent context, so the chart
  always reached the partial. The test failure that surfaced it
  was an assertion typo (expected `... || {})` where the template
  has `... || {}}`), not a rendering gap.
- **Test-trim pass** — review of the session's new tests found one
  dead key and several redundancies, all removed: the
  `display_unit_count` context key in `_visual_context` (no
  template consumes it — the card renders `display_unit_label`
  only) plus its assertion and the static-label assertion in
  `test_detail_view_missing_value_date_renders_today`;
  `test_execute_rejects_flat_params` (pinned django-glue's negative
  contract; the template pin + positive endpoint test already guard
  the regression); `DisplayWindowRangeTestCase` 8 → 5 (dropped the
  three `count_two` variants — the count parameter is already
  exercised by the distinct 8/12/13 defaults and the from-sunday
  case); `IntervalRangeTestCase` 10 → 9 (dropped a second Saturday
  case that duplicated `test_weekly_range_from_saturday` one week
  earlier); the three per-interval `display_window` default tests
  merged into `test_display_window_defaults_per_interval` (the
  per-interval date math is already pinned in
  `DisplayWindowRangeTestCase`, two of the three were identical
  calls, and the service tests only needed to pin interval
  resolution + default count). Metric suite 528 passed after the
  trim.

### A3 — done

- `VisualPieChart` stays a filled pie (no donut — user
  decision): the series gets `center: ['50%', '45%']`
  (slight upward nudge so the pie clears the bottom legend)
  and an explicit `label: {'show': True}` (the original plan
  hid the slice labels to avoid the card-header collision;
  reversed — labels stay shown). Legend settled on
  constrained wrapping — `default_legend = {'bottom': 0,
  'left': 'center', 'width': '90%'}` — after the browser
  rejected a bottom scroll legend (auto-width scroll legends
  never page without an explicit width, and the paging
  arrows were hard to discover) and a vertical right-edge
  column (long slug labels make the column wide). Overriding
  `default_legend` (not `legend`) keeps the base `bottom: 30`
  default from leaking through the merge — the first
  vertical-legend attempt shipped with the stale `bottom: 30`
  and failed its own test. The new option keys are not pinned
  in the tests (user decision — cosmetic layout, verified
  visually); the pie tests stay data-shape only.

### A5 — done

- `no_matching_data()` on the transformation service: true
  only when references are set, the patterns match zero
  values (all-time), and the statistic has values at all.
  Cached under `_cache_key('no-match')` — the key embeds the
  reference list + value revision, so adding references or
  new values invalidates it; all-time by design (ignores
  `value_date`).
- Both `render_context()` and the detail view's
  `_visual_context` pass the flag and **suppress
  `current_condition`** when it is true — the existing grey
  "No Data" state renders unchanged (grey badge, transparent
  indicator circle; no badge markup edits) and the header
  keeps showing 0 (a true in-window zero); only the false
  red badge is replaced.
- `visual.html`: chart branch gains a "No matching data" line
  under the chart; the indicator's no-condition caption
  switches from "No condition matches the current value" to
  "No matching data". `detail_card.html` passes the key in
  its include `with` clause (the other consumers pass the
  full context dict through).
- Tests: +3 service (off without references / off for empty
  statistic / render_context suppression), +2 view (caption
  shown / absent). In the test-trim reviews, two service
  tests were dropped as strict subsumptions of the view
  tests: "off with any match" (the matching-reference view
  test asserts the flag is False for that scenario) and
  "flag fires" (the detail-view test asserts the flag is
  True for that scenario). Signage query-count
  test 10 → 13: the flag adds one reference-list query per
  visual per render (the guard runs before the cache
  lookup); the test's flat-structural intent is unchanged.
  Metric suite 534 passed.
- **A5 follow-up (surface gap + include simplification)** —
  reviewing the `visual.html` include sites found the flag
  only reached the detail page: every consumer re-enumerates
  keys in an explicit `with` list, and three of them dropped
  `no_matching_data` (region tag dict + `region_visual.html`,
  `display_page.html`, `section_card.html`), so those
  surfaces showed the grey badge with the wrong caption.
  Fixed: the region inclusion tag now returns the key,
  `display_page.html` forwards `section.no_matching_data`
  (its list is load-bearing — it renames loop variables), and
  the three purely-redundant `with` lists (detail card,
  region visual, presentation section card) were dropped for
  bare includes — without `only` the include inherits the
  parent context anyway, so new `render_context()` keys now
  flow to those surfaces automatically. Regression test:
  `test_django_spire_metric_region.py::test_no_matching_data_renders_caption`
  (tag → include → caption end-to-end). Metric 535 + core 358
  passed after the follow-up.
- **Indicator geometry aligned with the pie** — the indicator
  branch of `visual.html` was flow layout (`.mt-6` circle with a
  `40cqh` diameter — resolving against the *viewport* on
  non-signage surfaces, which have no `container-type` ancestor —
  plus a `.mt-5` caption). It now mirrors the chart box
  structurally: a `position-relative` box with the same style as
  `chart.html` (`flex: 1 1 auto; min-height: 95%; width: 100%`)
  plus `container-type: size`, so the circle/caption cqw/cqh units
  resolve against the same box the ECharts canvas occupies.
  Circle: centered at `top: 45%` (the pie's `center: ['50%','45%']`)
  with diameter `min(60cqw, 60cqh)` — between the original
  (~40cqh) and the pie's 75% default, per user tuning (smaller than
  the pie, larger than before); the icon scales with it
  (`min(30cqw, 30cqh)`, the prior 50% ratio). The state
  caption (badge + text, including the A5 "No matching data" line)
  sits at `bottom: 10%; left: 50%; width: 90%` — a raised variant
  of the pie's legend placement (`bottom: 0`), per user request.
  No Data transparent-circle behavior unchanged. Template only;
  no test changes (nothing pins this markup; the A5 caption-string
  tests still hold).
- **X-axis rebuilt as one category label per unit (kiosk)** —
  the line/bar/area charts used `xAxis: {'type': 'time'}`,
  which is wrong for these fixed-N-unit windows: ECharts
  places time ticks at *nice time points* (month boundaries),
  not at our units, so on the kiosk the month names collided
  with adjacent day numbers ("29Aug"/"29Sep"). First fix was
  `axisLabel.hideOverlap: true` (off by default in 6.1.0 —
  verified in the shipped bundle, with it falsy only the
  first/last label pairs are checked) — that removed the
  collision but dropped all month context and left a cramped
  month-boundary tick ("5 8"), so the axis was replaced:
  `_unit_x_axis()` now returns `{'type': 'category', 'data':
  [<one label per unit>], 'axisLabel': {'hideOverlap': True}}`
  and the series data is plain values aligned to that frame
  (all references share the unit frame, so index alignment
  holds). `_unit_label()`: daily/weekly → "May 10" (unit
  start), monthly → "May", with a two-digit year appended
  ("Jan 26") when a 13-month window crosses into a second
  year.   `hideOverlap` stays as the fallback for narrow cards.
  The kiosk theme patch keeps the key (it spreads the existing
  `axisLabel`). Line/bar/execute-endpoint test expectations
  updated to the category axis + plain values.
  Follow-up: the kiosk screenshot then showed the *y* axis
  with the same disease (0–18 in ten ticks at kiosk font
  stacked on each other) — the base `Chart._build_option`
  now emits `yAxis: {'type': 'value', 'axisLabel':
  {'hideOverlap': True}}` for all grid charts (framework
  safety net, no-op when labels fit); pinned in
  `test_line_chart_option`.
- **Kiosk pie labels restored (with protection)** — the kiosk
  theme patch in `display_page.html` (added 2026-09-21 in
  `a77e8d6e`, the scaling overhaul) had been force-hiding pie
  labels (`label.show = false`) so un-truncated reference
  names couldn't break the wall layout. Now: the 28-char
  truncator is extracted into a `truncate()` helper shared by
  the legend and pie labels; the pie branch sets
  `show: true`, `formatter: truncate(params.name)`,
  `overflow: 'truncate'` + `width: 35%` of the canvas
  (ECharts-level ellipsis, computable only client-side), and
  `labelLayout.hideOverlap: true` so crowded pies drop
  overlapping labels. No slice-count gate — a many-slice pie
  shows whatever fits, legend still below. Inline template
  JS (no test coverage; verified visually).
- **A2 — gauge value, reference, scale** —
  - Scale fix: `gauge_max()` short-circuits
    `if self._is_percentage(): return 100` before the
    condition/value fallbacks — a 5% gauge no longer gets
    max 10 (needle dead center); conditions now sit at
    meaningful positions (target 10 = the 10% mark). Low
    rates sit near the bottom: honest over zoomed.
  - Layout: value centered (`detail.offsetCenter
    ['0%','0%']`), reference ratio at the bottom
    (`title.offsetCenter ['0%','70%']`).
  - Value-type rule: the server pre-computes both strings
    per data item via `format_statistic_value` —
    `detail` = the formatted value (`12.34%`,
    `$1,234.50`, `1,234`), `reference` =
    `value / max × 100` at 1 decimal (`83.3%`) for
    number/currency only; percentage gauges omit it and
    set `title.show: false`. ECharts formatters are
    functions and cannot travel in the JSON payload, so
    `chart.html` injects them once at init (reading
    `params.data.detail` / `params.data.reference`); a
    no-statistic gauge ships empty data and the formatters
    are never invoked.
  - Tests: `test_gauge_max_is_100_for_percentage`
    (with conditions — the short-circuit is a single line,
    so the without-conditions variant is a strict
    subsumption), gauge chart-option asserts extended to
    the detail/title dicts + item strings, plus a
    percentage chart-option test (max 100, `12.34%`, no
    reference, title hidden). Metric + core 894 passed.
- **A2 follow-up (needle z-order + update-path formatters)** —
  - The gauge pointer drew over the center value: `detail`
    and `title` now carry `z: 10` so both text layers sit
    above the needle.
  - The Glue polling path (`_update()` in `chart.html`)
    re-sets the option with `notMerge: true` from the JSON
    payload, which carries no functions — after the first
    poll the gauge reverted to the raw `{value}` center
    (no `%`/`$` label, so it no longer matched the card
    header) and the name instead of the ratio. The
    formatter injection was extracted to
    `_inject_gauge_formatters(option)` and is now applied
    in both `init()` and `_update()`.
- **A2 follow-up (ECharts gauge contract + 0–100 scale)** —
  Read the shipped ECharts 6.1.0 `GaugeView` source; three
  hard facts reshaped the design:
  - `detail.formatter(fn)` is called with the **raw value
    number only** — `params.data` never exists, so the
    earlier `params.data?.detail` always fell through to
    `String(params.value ?? 0)` → `'0'` (the reported
    0-in-the-middle). The detail text is now formatted
    client-side in `_gauge_detail_formatter(value_type)`,
    mirroring `format_statistic_value` (percentage
    `51.12%`, currency `-$1,234.50`, number `1,234.5`);
    `valueType` rides in the series payload (ECharts
    ignores unknown keys) and the count-up animation
    formats interpolated values cleanly.
  - The gauge **title never calls a formatter** — it
    always renders the data item's `name`. The reference
    ratio now rides in `name` (e.g. `50.0%`); percentage
    gauges hide the title, where the label stays the
    name.
  - Title/detail `z2` is hard-coded from
    `pointer.showAbove` (0 or 2) and the pointer renders
    last — **no option puts text above the needle**; the
    `z: 10` experiment was dead config and is removed.
    Needle restored (user choice); the slight overlap
    with the center value is accepted.
  - **All gauges are now 0–100** (user decision,
    overriding the type-conditional scale):
    `gauge_max()` returns `100` unconditionally — the
    conditions still color the arc/state but no longer
    set the ceiling. The three old gauge_max tests
    (250-from-conditions, 80-value-fallback,
    100-percentage) collapsed to one
    `test_gauge_max_is_100`; the chart-option test keeps
    a 60-ceiling condition and asserts max 100 to pin
    the override. Metric + core 892 passed.
- **A2 follow-up (legend + reference label restored)** —
  The hidden legend was overreach: the gauge legend had
  always shown the reference label, and moving the ratio
  into `name` cost the legend that label. Restored:
  `VisualGaugeChart` no longer hides the legend; each data
  item carries `label` (the reference name) alongside
  `name` (the ratio), and `chart.html` injects a
  `legend.formatter` mapping name→label (functions can't
  ride in the JSON payload) — so the legend shows the
  reference label again while the title keeps the A2
  ratio. Metric + core 892 passed.
