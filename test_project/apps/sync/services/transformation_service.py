from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

from typing_extensions import TYPE_CHECKING

from django_spire.contrib.service import BaseDjangoModelService

from test_project.apps.sync import models
from test_project.apps.sync.config import get_active_tablet_databases
from test_project.apps.sync.constants import (
    TRUNCATE_LIMIT,
    FieldOutcome,
    MergedOutcome,
    RecordKind,
    SyncModelLabel,
    VerificationStatus,
    WinnerSide,
)
from test_project.apps.sync.context import get_current_database, get_tablet_count, switch_database
from test_project.apps.sync.registry import (
    DISPLAY_FIELDS,
    FOREIGN_KEY_DISPLAY,
    LABEL_MAP,
    LABEL_TO_DISPLAY,
    MODEL_ORDER,
)
from test_project.apps.sync.types import (
    CellData,
    ClassifiedRow,
    CloudDatabaseView,
    CloudRecord,
    CloudRecordField,
    CloudSection,
    FieldDisplay,
    HybridLogicalClockDecoded,
    MergedCellData,
    MergedCloudRecord,
    MergedCloudRecordField,
    SyncCounts,
    SyncPerformResult,
    VerificationField,
    VerificationRecord,
    VerificationResult,
    VerificationSection,
)

if TYPE_CHECKING:
    from typing_extensions import Any

    from test_project.apps.sync.models import Client


_COUNTER_BITS = 16

_MODEL_MAP: dict[str, type] = {
    'Client': models.Client,
    'Site': models.Site,
    'Stake': models.Stake,
    'SurveyPlan': models.SurveyPlan,
}


def _coerce_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


class SyncTransformationService(BaseDjangoModelService['Client']):
    obj: Client

    def apply_resolutions(self, rows: list[ClassifiedRow], result: SyncPerformResult, tablet_database: str = '') -> None:
        tablet_data = result.tablets.get(tablet_database)

        if not tablet_data:
            return

        conflict_map = {}

        for entry in tablet_data.tablet_result.conflict_log:
            conflict_map[entry.key] = entry

        for row in rows:
            resolution = conflict_map.get(row.id)

            if resolution:
                row.resolution = resolution

                tablet_outcomes: dict[str, str] = {}
                cloud_outcomes: dict[str, str] = {}

                for field_conflict in resolution.field_conflicts:
                    field_name = field_conflict.field_name

                    if field_conflict.winner == WinnerSide.REMOTE:
                        tablet_outcomes[field_name] = FieldOutcome.WON
                        cloud_outcomes[field_name] = FieldOutcome.LOST
                    else:
                        tablet_outcomes[field_name] = FieldOutcome.LOST
                        cloud_outcomes[field_name] = FieldOutcome.WON

                row.tablet_cell = self._build_cell(
                    row.tablet_object, row.model, row.difference_fields, tablet_outcomes,
                )
                row.cloud_cell = self._build_cell(
                    row.cloud_object, row.model, row.difference_fields, cloud_outcomes,
                )

            row.merged_cell = self._build_merged_cell(row, resolution)

    def build_cloud_database_view(self) -> CloudDatabaseView:
        current_database = get_current_database()
        switch_database('cloud')

        sections = []
        total_records = 0

        for model_name in MODEL_ORDER:
            model_class = _MODEL_MAP[model_name]
            fields = DISPLAY_FIELDS.get(model_name, ())
            foreign_key_display = FOREIGN_KEY_DISPLAY.get(model_name, [])
            objects = list(model_class.objects.select_related().all())
            records = []

            for instance in objects:
                total_records += 1
                timestamp_map = instance.sync_field_timestamps if hasattr(instance, 'sync_field_timestamps') and instance.sync_field_timestamps else {}
                record_fields = []

                for foreign_key_name, foreign_key_function in foreign_key_display:
                    foreign_key_value = str(foreign_key_function(instance))
                    foreign_key_display_value = foreign_key_value if len(foreign_key_value) <= TRUNCATE_LIMIT else foreign_key_value[:TRUNCATE_LIMIT - 3] + '...'

                    record_fields.append(CloudRecordField(
                        full_value=foreign_key_value if foreign_key_value != foreign_key_display_value else '',
                        name=foreign_key_name,
                        timestamp=self.decode_hybrid_logical_clock(timestamp_map.get(foreign_key_name, 0)),
                        value=foreign_key_display_value,
                    ))

                for field_name in fields:
                    raw_value = _coerce_value(getattr(instance, field_name, ''))
                    full_string = str(raw_value)
                    display_value = full_string if len(full_string) <= TRUNCATE_LIMIT else full_string[:TRUNCATE_LIMIT - 3] + '...'

                    if raw_value == '' or raw_value is None:
                        display_value = '\u2014'
                        full_string = ''

                    record_fields.append(CloudRecordField(
                        full_value=full_string if full_string != display_value else '',
                        name=field_name,
                        timestamp=self.decode_hybrid_logical_clock(timestamp_map.get(field_name, 0)),
                        value=display_value,
                    ))

                records.append(CloudRecord(
                    fields=record_fields,
                    id=str(instance.id),
                    sync_field_last_modified=self.decode_hybrid_logical_clock(instance.sync_field_last_modified),
                    title=str(instance),
                ))

            sections.append(CloudSection(
                model_name=model_name,
                record_count=len(records),
                records=records,
            ))

        switch_database(current_database)

        return CloudDatabaseView(
            sections=sections,
            total_records=total_records,
        )

    def build_merged_cloud_view(self, result: SyncPerformResult) -> list[MergedCloudRecord]:
        current_database = get_current_database()

        field_sources: dict[str, dict[str, dict[str, str]]] = {}

        for tablet_database, tablet_data in result.tablets.items():
            tablet_result = tablet_data.tablet_result

            for category in ('created', 'applied', 'compatible'):
                for label, keys in getattr(tablet_result, category).items():
                    for key in keys:
                        sources = field_sources.setdefault(label, {}).setdefault(key, {})
                        sources['_default'] = tablet_database

            for entry in tablet_result.conflict_log:
                label = entry.model_label
                key = entry.key
                sources = field_sources.setdefault(label, {}).setdefault(key, {})

                for field_conflict in entry.field_conflicts:
                    if field_conflict.winner == WinnerSide.REMOTE:
                        sources[field_conflict.field_name] = tablet_database
                    else:
                        sources[field_conflict.field_name] = WinnerSide.CLOUD

        switch_database('cloud')

        label_order = result.sync_order or list(LABEL_TO_DISPLAY.keys())
        records: list[MergedCloudRecord] = []

        for label in label_order:
            display_name = LABEL_TO_DISPLAY.get(label, label)
            model_class = LABEL_MAP.get(label)

            if not model_class:
                continue

            display_fields = DISPLAY_FIELDS.get(display_name, ())
            foreign_key_display = FOREIGN_KEY_DISPLAY.get(display_name, [])

            for instance in model_class.objects.select_related().all():
                key = str(instance.id)
                record_sources = field_sources.get(label, {}).get(key, {})
                default_source = record_sources.get('_default', WinnerSide.CLOUD)

                fields = []

                for foreign_key_name, foreign_key_function in foreign_key_display:
                    source = record_sources.get(foreign_key_name, default_source)
                    fields.append(MergedCloudRecordField(
                        name=foreign_key_name,
                        source=source,
                        value=str(foreign_key_function(instance)),
                    ))

                for field_name in display_fields:
                    source = record_sources.get(field_name, default_source)
                    raw_value = _coerce_value(getattr(instance, field_name, ''))
                    value_string = str(raw_value) if raw_value != '' and raw_value is not None else '\u2014'
                    fields.append(MergedCloudRecordField(
                        name=field_name,
                        source=source,
                        value=value_string,
                    ))

                records.append(MergedCloudRecord(
                    fields=fields,
                    id=key,
                    model=display_name,
                    title=str(instance),
                ))

        switch_database(current_database)
        return records

    def build_verification(self) -> VerificationResult:
        current_database = get_current_database()
        tablet_count = get_tablet_count()
        tablet_databases = get_active_tablet_databases(tablet_count)

        tablet_sections: dict[str, list[VerificationSection]] = {}
        total_matched = 0
        total_mismatched = 0
        total_records = 0

        switch_database('cloud')
        cloud_data: dict[str, dict[str, Any]] = {}

        for model_name in MODEL_ORDER:
            model_class = _MODEL_MAP[model_name]
            cloud_data[model_name] = {
                str(instance.id): instance
                for instance in model_class.objects.select_related().all()
            }

        for tablet_database in tablet_databases:
            switch_database(tablet_database)
            sections = []

            for model_name in MODEL_ORDER:
                model_class = _MODEL_MAP[model_name]
                fields = DISPLAY_FIELDS.get(model_name, ())
                foreign_key_display = FOREIGN_KEY_DISPLAY.get(model_name, [])

                tablet_objects = list(model_class.objects.select_related().all())
                tablet_map = {str(instance.id): instance for instance in tablet_objects}
                cloud_map = cloud_data[model_name]

                all_ids = list(dict.fromkeys(list(tablet_map.keys()) + list(cloud_map.keys())))
                records = []

                for record_id in all_ids:
                    tablet = tablet_map.get(record_id)
                    cloud = cloud_map.get(record_id)

                    if tablet and not cloud:
                        total_records += 1
                        total_mismatched += 1
                        records.append(VerificationRecord(
                            fields=[],
                            id=record_id,
                            status=VerificationStatus.TABLET_ONLY,
                            title=str(tablet),
                        ))
                        continue

                    if cloud and not tablet:
                        total_records += 1
                        total_mismatched += 1
                        records.append(VerificationRecord(
                            fields=[],
                            id=record_id,
                            status=VerificationStatus.CLOUD_ONLY,
                            title=str(cloud),
                        ))
                        continue

                    total_records += 1
                    field_rows = []
                    has_mismatch = False

                    for foreign_key_name, foreign_key_function in foreign_key_display:
                        tablet_value = str(foreign_key_function(tablet))
                        cloud_value = str(foreign_key_function(cloud))
                        matched = tablet_value == cloud_value

                        if not matched:
                            has_mismatch = True

                        field_rows.append(VerificationField(
                            cloud_value=cloud_value,
                            matched=matched,
                            name=foreign_key_name,
                            tablet_value=tablet_value,
                        ))

                    for field_name in fields:
                        tablet_value = str(_coerce_value(getattr(tablet, field_name, '')))
                        cloud_value = str(_coerce_value(getattr(cloud, field_name, '')))
                        matched = tablet_value == cloud_value

                        if not matched:
                            has_mismatch = True

                        field_rows.append(VerificationField(
                            cloud_value=cloud_value,
                            matched=matched,
                            name=field_name,
                            tablet_value=tablet_value,
                        ))

                    if has_mismatch:
                        total_mismatched += 1
                    else:
                        total_matched += 1

                    records.append(VerificationRecord(
                        fields=field_rows,
                        id=record_id,
                        status=VerificationStatus.MATCH if not has_mismatch else VerificationStatus.MISMATCH,
                        title=str(tablet),
                    ))

                sections.append(VerificationSection(
                    matched=sum(1 for record in records if record.status == VerificationStatus.MATCH),
                    mismatched=sum(1 for record in records if record.status != VerificationStatus.MATCH),
                    model_name=model_name,
                    record_count=len(all_ids),
                    records=records,
                ))

            tablet_sections[tablet_database] = sections

        switch_database(current_database)

        return VerificationResult(
            tablet_sections=tablet_sections,
            total_matched=total_matched,
            total_mismatched=total_mismatched,
            total_records=total_records,
            verified=total_mismatched == 0 and total_records > 0,
        )

    def classify_databases(self, tablet_database: str = '') -> list[ClassifiedRow]:
        current_database = get_current_database()

        if not tablet_database:
            tablet_database = current_database if current_database != 'cloud' else 'tablet_1'

        switch_database(tablet_database)
        tablet_clients = list(models.Client.objects.all())
        tablet_sites = list(models.Site.objects.select_related('client').all())
        tablet_plans = list(models.SurveyPlan.objects.select_related('site').all())
        tablet_stakes = list(models.Stake.objects.select_related('survey_plan', 'survey_plan__site').all())

        switch_database('cloud')
        cloud_clients = list(models.Client.objects.all())
        cloud_sites = list(models.Site.objects.select_related('client').all())
        cloud_plans = list(models.SurveyPlan.objects.select_related('site').all())
        cloud_stakes = list(models.Stake.objects.select_related('survey_plan', 'survey_plan__site').all())

        switch_database(current_database)

        all_rows: list[ClassifiedRow] = []
        all_rows.extend(self._classify_records(tablet_clients, cloud_clients, 'Client'))
        all_rows.extend(self._classify_records(tablet_sites, cloud_sites, 'Site'))
        all_rows.extend(self._classify_records(tablet_plans, cloud_plans, 'SurveyPlan'))
        all_rows.extend(self._classify_records(tablet_stakes, cloud_stakes, 'Stake'))

        return all_rows

    @staticmethod
    def count_kinds(rows: list[ClassifiedRow]) -> SyncCounts:
        counts = SyncCounts()

        for row in rows:
            setattr(counts, row.kind, getattr(counts, row.kind) + 1)

        return counts

    @staticmethod
    def decode_hybrid_logical_clock(hybrid_logical_clock: int) -> HybridLogicalClockDecoded:
        if not hybrid_logical_clock:
            return HybridLogicalClockDecoded(counter=0, human='', raw='', wall_ms=0)

        wall_ms = hybrid_logical_clock >> _COUNTER_BITS
        counter = hybrid_logical_clock & ((1 << _COUNTER_BITS) - 1)
        datetime_utc = datetime.fromtimestamp(wall_ms / 1000, tz=timezone.utc)

        return HybridLogicalClockDecoded(
            counter=counter,
            human=datetime_utc.strftime('%Y-%m-%d %H:%M:%S.') + f'{datetime_utc.microsecond // 1000:03d}',
            raw=str(hybrid_logical_clock),
            wall_ms=wall_ms,
        )

    def _build_cell(
        self,
        instance: Any,
        model_name: str,
        difference_fields: list,
        field_outcomes: dict | None = None,
    ) -> CellData | None:
        if instance is None:
            return None

        timestamp_map = instance.sync_field_timestamps if hasattr(instance, 'sync_field_timestamps') and instance.sync_field_timestamps else {}
        fields = []

        for foreign_key_name, foreign_key_function in FOREIGN_KEY_DISPLAY.get(model_name, []):
            foreign_key_value = foreign_key_function(instance)
            foreign_key_string = str(foreign_key_value)
            foreign_key_display_value = foreign_key_string if len(foreign_key_string) <= TRUNCATE_LIMIT else foreign_key_string[:TRUNCATE_LIMIT - 3] + '...'

            fields.append(FieldDisplay(
                full_value=foreign_key_string if foreign_key_string != foreign_key_display_value else '',
                is_diff=False,
                name=foreign_key_name,
                outcome='',
                timestamp=self.decode_hybrid_logical_clock(timestamp_map.get(foreign_key_name, 0)),
                value=foreign_key_display_value,
            ))

        for field_name in DISPLAY_FIELDS.get(model_name, ()):
            raw_value = _coerce_value(getattr(instance, field_name, ''))
            full_string = str(raw_value)
            display_value = full_string if len(full_string) <= TRUNCATE_LIMIT else full_string[:TRUNCATE_LIMIT - 3] + '...'

            if raw_value == '' or raw_value is None:
                display_value = '\u2014'
                full_string = ''

            outcome = ''

            if field_outcomes and field_name in field_outcomes:
                outcome = field_outcomes[field_name]

            fields.append(FieldDisplay(
                full_value=full_string if full_string != display_value else '',
                is_diff=field_name in difference_fields,
                name=field_name,
                outcome=outcome,
                timestamp=self.decode_hybrid_logical_clock(timestamp_map.get(field_name, 0)),
                value=display_value,
            ))

        return CellData(
            fields=fields,
            title=str(instance),
        )

    def _build_merged_cell(self, row: ClassifiedRow, resolution: Any) -> MergedCellData | None:
        kind = row.kind

        if kind == RecordKind.MATCH:
            cell = row.tablet_cell
            return MergedCellData(
                fields=[replace(field, outcome=FieldOutcome.MATCH) for field in cell.fields],
                outcome=MergedOutcome.MATCH,
                title=cell.title,
            )

        if kind == RecordKind.TABLET_ONLY:
            cell = row.tablet_cell
            return MergedCellData(
                fields=[replace(field, outcome=FieldOutcome.PUSHED) for field in cell.fields],
                outcome=MergedOutcome.PUSHED,
                title=cell.title,
            )

        if kind == RecordKind.CLOUD_ONLY:
            cell = row.cloud_cell
            return MergedCellData(
                fields=[replace(field, outcome=FieldOutcome.PULLED) for field in cell.fields],
                outcome=MergedOutcome.PULLED,
                title=cell.title,
            )

        if kind == RecordKind.CONFLICT and resolution:
            winner_map = {}

            for field_conflict in resolution.field_conflicts:
                field_name = field_conflict.field_name
                winner_map[field_name] = WinnerSide.LOCAL if field_conflict.winner == WinnerSide.REMOTE else WinnerSide.CLOUD

            tablet_cell = row.tablet_cell
            cloud_cell = row.cloud_cell
            merged_fields = []

            for local_field in tablet_cell.fields:
                field_name = local_field.name

                if field_name in winner_map:
                    winner_side = winner_map[field_name]

                    if winner_side == WinnerSide.LOCAL:
                        merged_fields.append(replace(local_field, is_diff=True, outcome=FieldOutcome.WON_LOCAL))
                    else:
                        cloud_field = next((field for field in cloud_cell.fields if field.name == field_name), local_field)
                        merged_fields.append(replace(cloud_field, is_diff=True, outcome=FieldOutcome.WON_CLOUD))
                else:
                    merged_fields.append(replace(local_field, is_diff=False, outcome=''))

            return MergedCellData(
                fields=merged_fields,
                outcome=MergedOutcome.RESOLVED,
                title=tablet_cell.title,
            )

        return None

    def _classify_records(self, tablet_objects: list, cloud_objects: list, model_name: str) -> list[ClassifiedRow]:
        tablet_map = {str(instance.id): instance for instance in tablet_objects}
        cloud_map = {str(instance.id): instance for instance in cloud_objects}
        all_ids = list(dict.fromkeys(list(tablet_map.keys()) + list(cloud_map.keys())))

        rows = []

        for record_id in all_ids:
            tablet = tablet_map.get(record_id)
            cloud = cloud_map.get(record_id)

            difference_fields = []

            if tablet and cloud:
                for key in DISPLAY_FIELDS.get(model_name, ()):
                    tablet_value = _coerce_value(getattr(tablet, key, ''))
                    cloud_value = _coerce_value(getattr(cloud, key, ''))

                    if str(tablet_value) != str(cloud_value):
                        difference_fields.append(key)

                kind = RecordKind.CONFLICT if difference_fields else RecordKind.MATCH
            elif tablet:
                kind = RecordKind.TABLET_ONLY
            else:
                kind = RecordKind.CLOUD_ONLY

            rows.append(ClassifiedRow(
                cloud_cell=self._build_cell(cloud, model_name, difference_fields),
                cloud_object=cloud,
                difference_count=len(difference_fields),
                difference_fields=difference_fields,
                id=record_id,
                kind=kind,
                merged_cell=None,
                model=model_name,
                resolution=None,
                tablet_cell=self._build_cell(tablet, model_name, difference_fields),
                tablet_object=tablet,
            ))

        return rows
