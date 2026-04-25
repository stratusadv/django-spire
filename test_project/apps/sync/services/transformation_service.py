from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from test_project.apps.sync import models
from test_project.apps.sync.config import get_active_tablet_databases
from test_project.apps.sync.context import get_current_db, get_tablet_count, switch_db


DISPLAY_FIELDS = {
    'Client': ('name', 'contact_name', 'contact_email'),
    'Site': ('name', 'description', 'region', 'status'),
    'SurveyPlan': (
        'plan_number',
        'stake_spacing_m', 'line_direction', 'headland_offset_m', 'office_notes',
        'baseline_a_latitude', 'baseline_a_longitude',
        'baseline_b_latitude', 'baseline_b_longitude',
        'heading_degrees', 'crew_notes',
        'status',
    ),
    'Stake': (
        'latitude', 'longitude', 'elevation', 'is_placed',
        'stake_type', 'label',
    ),
}

FK_DISPLAY = {
    'Site': [('client', lambda obj: obj.client.name if obj.client else '')],
    'SurveyPlan': [('site', lambda obj: obj.site.name if obj.site else '')],
    'Stake': [('survey_plan', lambda obj: str(obj.survey_plan) if obj.survey_plan else '')],
}

MODEL_ORDER = ['Client', 'Site', 'SurveyPlan', 'Stake']

MODEL_MAP = {
    'Client': models.Client,
    'Site': models.Site,
    'SurveyPlan': models.SurveyPlan,
    'Stake': models.Stake,
}

TRUNCATE_LIMIT = 40

_COUNTER_BITS = 16


def _coerce_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


class SyncTransformationService:
    def apply_resolutions(self, rows: list[dict], result: dict, tablet_db: str = '') -> None:
        tablet_data = result.get('tablets', {}).get(tablet_db, {})
        conflict_map = {}

        for entry in tablet_data.get('tablet_result', {}).get('conflict_log', []):
            conflict_map[entry['key']] = entry

        for row in rows:
            resolution = conflict_map.get(row['id'])

            if resolution:
                row['resolution'] = resolution

                tablet_outcomes = {}
                cloud_outcomes = {}

                for fc in resolution.get('field_conflicts', []):
                    fname = fc['field_name']

                    if fc['winner'] == 'remote':
                        tablet_outcomes[fname] = 'won'
                        cloud_outcomes[fname] = 'lost'
                    else:
                        tablet_outcomes[fname] = 'lost'
                        cloud_outcomes[fname] = 'won'

                row['tablet_cell'] = self._build_cell(
                    row['tablet_obj'], row['model'], row['diff_fields'], tablet_outcomes
                )
                row['cloud_cell'] = self._build_cell(
                    row['cloud_obj'], row['model'], row['diff_fields'], cloud_outcomes
                )

            row['merged_cell'] = self._build_merged_cell(row, resolution)

    def build_cloud_database_view(self) -> dict[str, Any]:
        current_db = get_current_db()
        switch_db('cloud')

        sections = []
        total_records = 0

        for model_name in MODEL_ORDER:
            model_cls = MODEL_MAP[model_name]
            fields = DISPLAY_FIELDS.get(model_name, ())
            fk_display = FK_DISPLAY.get(model_name, [])
            objects = list(model_cls.objects.select_related().all())
            records = []

            for obj in objects:
                total_records += 1
                ts_map = obj.sync_field_timestamps if hasattr(obj, 'sync_field_timestamps') and obj.sync_field_timestamps else {}
                record_fields = []

                for fk_name, fk_fn in fk_display:
                    fk_val = str(fk_fn(obj))
                    fk_display_val = fk_val if len(fk_val) <= TRUNCATE_LIMIT else fk_val[:TRUNCATE_LIMIT - 3] + '...'

                    record_fields.append({
                        'name': fk_name,
                        'value': fk_display_val,
                        'full_value': fk_val if fk_val != fk_display_val else '',
                        'ts': self.decode_hlc(ts_map.get(fk_name, 0)),
                    })

                for f in fields:
                    raw_val = _coerce_value(getattr(obj, f, ''))
                    full_str = str(raw_val)
                    display_val = full_str if len(full_str) <= TRUNCATE_LIMIT else full_str[:TRUNCATE_LIMIT - 3] + '...'

                    if raw_val == '' or raw_val is None:
                        display_val = '\u2014'
                        full_str = ''

                    record_fields.append({
                        'name': f,
                        'value': display_val,
                        'full_value': full_str if full_str != display_val else '',
                        'ts': self.decode_hlc(ts_map.get(f, 0)),
                    })

                records.append({
                    'id': str(obj.id),
                    'title': str(obj),
                    'sync_field_last_modified': self.decode_hlc(obj.sync_field_last_modified),
                    'fields': record_fields,
                })

            sections.append({
                'model_name': model_name,
                'record_count': len(records),
                'records': records,
            })

        switch_db(current_db)

        return {
            'sections': sections,
            'total_records': total_records,
        }

    def build_merged_cloud_view(self, result: dict) -> list[dict]:
        current_db = get_current_db()

        label_to_display = {
            'sync.Client': 'Client',
            'sync.Site': 'Site',
            'sync.SurveyPlan': 'SurveyPlan',
            'sync.Stake': 'Stake',
        }

        label_to_model = {
            'sync.Client': models.Client,
            'sync.Site': models.Site,
            'sync.SurveyPlan': models.SurveyPlan,
            'sync.Stake': models.Stake,
        }

        field_sources: dict[str, dict[str, dict[str, str]]] = {}

        for tablet_db, tdata in result.get('tablets', {}).items():
            tr = tdata.get('tablet_result', {})

            for category in ('created', 'applied', 'compatible'):
                for label, keys in tr.get(category, {}).items():
                    for key in keys:
                        sources = field_sources.setdefault(label, {}).setdefault(key, {})
                        sources['_default'] = tablet_db

            for entry in tr.get('conflict_log', []):
                label = entry['model_label']
                key = entry['key']
                sources = field_sources.setdefault(label, {}).setdefault(key, {})

                for fc in entry.get('field_conflicts', []):
                    if fc['winner'] == 'remote':
                        sources[fc['field_name']] = tablet_db
                    else:
                        sources[fc['field_name']] = 'cloud'

        switch_db('cloud')

        label_order = result.get('sync_order', list(label_to_display.keys()))
        records = []

        for label in label_order:
            display_name = label_to_display.get(label, label)
            model_cls = label_to_model.get(label)

            if not model_cls:
                continue

            display_fields = DISPLAY_FIELDS.get(display_name, ())
            fk_display = FK_DISPLAY.get(display_name, [])

            for obj in model_cls.objects.select_related().all():
                key = str(obj.id)
                record_sources = field_sources.get(label, {}).get(key, {})
                default_source = record_sources.get('_default', 'cloud')

                fields = []

                for fk_name, fk_fn in fk_display:
                    source = record_sources.get(fk_name, default_source)
                    fields.append({
                        'name': fk_name,
                        'value': str(fk_fn(obj)),
                        'source': source,
                    })

                for f in display_fields:
                    source = record_sources.get(f, default_source)
                    raw_val = _coerce_value(getattr(obj, f, ''))
                    val_str = str(raw_val) if raw_val != '' and raw_val is not None else '\u2014'
                    fields.append({
                        'name': f,
                        'value': val_str,
                        'source': source,
                    })

                records.append({
                    'model': display_name,
                    'title': str(obj),
                    'id': key,
                    'fields': fields,
                })

        switch_db(current_db)
        return records

    def build_verification(self) -> dict:
        current_db = get_current_db()
        tablet_count = get_tablet_count()
        tablet_databases = get_active_tablet_databases(tablet_count)

        model_map = {
            'Client': models.Client,
            'Site': models.Site,
            'SurveyPlan': models.SurveyPlan,
            'Stake': models.Stake,
        }

        model_order = ['Client', 'Site', 'SurveyPlan', 'Stake']
        tablet_sections: dict[str, list] = {}
        total_records = 0
        total_matched = 0
        total_mismatched = 0

        switch_db('cloud')
        cloud_data: dict[str, dict[str, Any]] = {}

        for model_name in model_order:
            model_cls = model_map[model_name]
            cloud_data[model_name] = {
                str(obj.id): obj
                for obj in model_cls.objects.select_related().all()
            }

        for tablet_db in tablet_databases:
            switch_db(tablet_db)
            sections = []

            for model_name in model_order:
                model_cls = model_map[model_name]
                fields = DISPLAY_FIELDS.get(model_name, ())
                fk_display = FK_DISPLAY.get(model_name, [])

                tablet_objects = list(model_cls.objects.select_related().all())
                tablet_map = {str(obj.id): obj for obj in tablet_objects}
                cloud_map = cloud_data[model_name]

                all_ids = list(dict.fromkeys(
                    list(tablet_map.keys()) + list(cloud_map.keys())
                ))

                records = []

                for record_id in all_ids:
                    tablet = tablet_map.get(record_id)
                    cloud = cloud_map.get(record_id)

                    if tablet and not cloud:
                        total_records += 1
                        total_mismatched += 1
                        records.append({
                            'id': record_id,
                            'status': 'tablet_only',
                            'title': str(tablet),
                            'fields': [],
                        })
                        continue

                    if cloud and not tablet:
                        total_records += 1
                        total_mismatched += 1
                        records.append({
                            'id': record_id,
                            'status': 'cloud_only',
                            'title': str(cloud),
                            'fields': [],
                        })
                        continue

                    total_records += 1
                    field_rows = []
                    has_mismatch = False

                    for fk_name, fk_fn in fk_display:
                        tv = str(fk_fn(tablet))
                        cv = str(fk_fn(cloud))
                        matched = tv == cv

                        if not matched:
                            has_mismatch = True

                        field_rows.append({
                            'name': fk_name,
                            'tablet_value': tv,
                            'cloud_value': cv,
                            'matched': matched,
                        })

                    for f in fields:
                        tv = str(_coerce_value(getattr(tablet, f, '')))
                        cv = str(_coerce_value(getattr(cloud, f, '')))
                        matched = tv == cv

                        if not matched:
                            has_mismatch = True

                        field_rows.append({
                            'name': f,
                            'tablet_value': tv,
                            'cloud_value': cv,
                            'matched': matched,
                        })

                    if has_mismatch:
                        total_mismatched += 1
                    else:
                        total_matched += 1

                    records.append({
                        'id': record_id,
                        'status': 'match' if not has_mismatch else 'mismatch',
                        'title': str(tablet),
                        'fields': field_rows,
                    })

                sections.append({
                    'model_name': model_name,
                    'record_count': len(all_ids),
                    'matched': sum(1 for r in records if r['status'] == 'match'),
                    'mismatched': sum(1 for r in records if r['status'] != 'match'),
                    'records': records,
                })

            tablet_sections[tablet_db] = sections

        switch_db(current_db)

        return {
            'tablet_sections': tablet_sections,
            'total_matched': total_matched,
            'total_mismatched': total_mismatched,
            'total_records': total_records,
            'verified': total_mismatched == 0 and total_records > 0,
        }

    def classify_databases(self, tablet_db: str = '') -> list[dict]:
        current_db = get_current_db()

        if not tablet_db:
            tablet_db = current_db if current_db != 'cloud' else 'tablet_1'

        switch_db(tablet_db)
        tablet_clients = list(models.Client.objects.all())
        tablet_sites = list(models.Site.objects.select_related('client').all())
        tablet_plans = list(models.SurveyPlan.objects.select_related('site').all())
        tablet_stakes = list(models.Stake.objects.select_related('survey_plan', 'survey_plan__site').all())

        switch_db('cloud')
        cloud_clients = list(models.Client.objects.all())
        cloud_sites = list(models.Site.objects.select_related('client').all())
        cloud_plans = list(models.SurveyPlan.objects.select_related('site').all())
        cloud_stakes = list(models.Stake.objects.select_related('survey_plan', 'survey_plan__site').all())

        switch_db(current_db)

        all_rows = []
        all_rows.extend(self._classify_records(tablet_clients, cloud_clients, 'Client'))
        all_rows.extend(self._classify_records(tablet_sites, cloud_sites, 'Site'))
        all_rows.extend(self._classify_records(tablet_plans, cloud_plans, 'SurveyPlan'))
        all_rows.extend(self._classify_records(tablet_stakes, cloud_stakes, 'Stake'))

        return all_rows

    @staticmethod
    def count_kinds(rows: list[dict]) -> dict[str, int]:
        counts = {'match': 0, 'conflict': 0, 'tablet_only': 0, 'cloud_only': 0}

        for row in rows:
            counts[row['kind']] += 1

        return counts

    @staticmethod
    def decode_hlc(hlc: int) -> dict:
        if not hlc:
            return {'raw': '', 'human': '', 'wall_ms': 0, 'counter': 0}

        wall_ms = hlc >> _COUNTER_BITS
        counter = hlc & ((1 << _COUNTER_BITS) - 1)
        dt = datetime.fromtimestamp(wall_ms / 1000, tz=timezone.utc)

        return {
            'raw': str(hlc),
            'human': dt.strftime('%Y-%m-%d %H:%M:%S.') + f'{dt.microsecond // 1000:03d}',
            'wall_ms': wall_ms,
            'counter': counter,
        }

    def _build_cell(self, obj, model_name: str, diff_fields: list, field_outcomes: dict | None = None) -> dict | None:
        if obj is None:
            return None

        ts_map = obj.sync_field_timestamps if hasattr(obj, 'sync_field_timestamps') and obj.sync_field_timestamps else {}
        fields = []

        for fk_name, fk_fn in FK_DISPLAY.get(model_name, []):
            fk_val = fk_fn(obj)
            fk_str = str(fk_val)
            fk_display = fk_str if len(fk_str) <= TRUNCATE_LIMIT else fk_str[:TRUNCATE_LIMIT - 3] + '...'

            fields.append({
                'name': fk_name,
                'value': fk_display,
                'full_value': fk_str if fk_str != fk_display else '',
                'is_diff': False,
                'outcome': '',
                'ts': self.decode_hlc(ts_map.get(fk_name, 0)),
            })

        for f in DISPLAY_FIELDS.get(model_name, ()):
            raw_val = _coerce_value(getattr(obj, f, ''))
            full_str = str(raw_val)
            display_val = full_str if len(full_str) <= TRUNCATE_LIMIT else full_str[:TRUNCATE_LIMIT - 3] + '...'

            if raw_val == '' or raw_val is None:
                display_val = '\u2014'
                full_str = ''

            outcome = ''

            if field_outcomes and f in field_outcomes:
                outcome = field_outcomes[f]

            fields.append({
                'name': f,
                'value': display_val,
                'full_value': full_str if full_str != display_val else '',
                'is_diff': f in diff_fields,
                'outcome': outcome,
                'ts': self.decode_hlc(ts_map.get(f, 0)),
            })

        return {
            'title': str(obj),
            'fields': fields,
        }

    def _build_merged_cell(self, row: dict, resolution: dict | None) -> dict | None:
        kind = row['kind']

        if kind == 'match':
            cell = row['tablet_cell']
            return {
                'title': cell['title'],
                'outcome': 'match',
                'fields': [{**f, 'outcome': 'match'} for f in cell['fields']],
            }

        if kind == 'tablet_only':
            cell = row['tablet_cell']
            return {
                'title': cell['title'],
                'outcome': 'pushed',
                'fields': [{**f, 'outcome': 'pushed'} for f in cell['fields']],
            }

        if kind == 'cloud_only':
            cell = row['cloud_cell']
            return {
                'title': cell['title'],
                'outcome': 'pulled',
                'fields': [{**f, 'outcome': 'pulled'} for f in cell['fields']],
            }

        if kind == 'conflict' and resolution:
            winner_map = {}

            for fc in resolution.get('field_conflicts', []):
                fname = fc['field_name']
                winner_map[fname] = 'local' if fc['winner'] == 'remote' else 'cloud'

            tablet_cell = row['tablet_cell']
            cloud_cell = row['cloud_cell']
            merged_fields = []

            for lf in tablet_cell['fields']:
                fname = lf['name']

                if fname in winner_map:
                    winner_side = winner_map[fname]

                    if winner_side == 'local':
                        merged_fields.append({**lf, 'is_diff': True, 'outcome': 'won_local'})
                    else:
                        cf = next((f for f in cloud_cell['fields'] if f['name'] == fname), lf)
                        merged_fields.append({**cf, 'is_diff': True, 'outcome': 'won_cloud'})
                else:
                    merged_fields.append({**lf, 'outcome': '', 'is_diff': False})

            return {
                'title': tablet_cell['title'],
                'outcome': 'resolved',
                'fields': merged_fields,
            }

        return None

    def _classify_records(self, tablet_objects: list, cloud_objects: list, model_name: str) -> list[dict]:
        tablet_map = {str(obj.id): obj for obj in tablet_objects}
        cloud_map = {str(obj.id): obj for obj in cloud_objects}
        all_ids = list(dict.fromkeys(list(tablet_map.keys()) + list(cloud_map.keys())))

        rows = []

        for record_id in all_ids:
            tablet = tablet_map.get(record_id)
            cloud = cloud_map.get(record_id)

            diff_fields = []

            if tablet and cloud:
                for key in DISPLAY_FIELDS.get(model_name, ()):
                    tv = _coerce_value(getattr(tablet, key, ''))
                    cv = _coerce_value(getattr(cloud, key, ''))

                    if str(tv) != str(cv):
                        diff_fields.append(key)

                kind = 'conflict' if diff_fields else 'match'
            elif tablet:
                kind = 'tablet_only'
            else:
                kind = 'cloud_only'

            rows.append({
                'kind': kind,
                'id': record_id,
                'model': model_name,
                'diff_count': len(diff_fields),
                'diff_fields': diff_fields,
                'tablet_obj': tablet,
                'cloud_obj': cloud,
                'tablet_cell': self._build_cell(tablet, model_name, diff_fields),
                'cloud_cell': self._build_cell(cloud, model_name, diff_fields),
                'merged_cell': None,
                'resolution': None,
            })

        return rows
