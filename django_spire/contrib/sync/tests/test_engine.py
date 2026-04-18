from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

import pytest

from django_spire.contrib.sync.engine import Engine
from django_spire.contrib.sync.exceptions import SyncAbortedError
from django_spire.contrib.sync.parser.xml import XmlField, XmlListField, XmlParser


FIXTURES_DIR = Path(__file__).parent / 'fixtures'


UNIT_PARSER = XmlParser(
    record_path='.//Unit',
    fields=[
        XmlField(key='stock_number', path='StockNumber'),
        XmlField(key='mfr_serial_number', path='MfrSerialNumber'),
        XmlField(key='type', path='Type'),
        XmlField(key='manufacturer', path='Manufacturer'),
        XmlField(key='description', path='Description'),
        XmlField(key='make_name', path='MakeName'),
        XmlField(key='model_name', path='ModelName'),
        XmlField(key='year', path='Year', cast=int, default='0'),
        XmlField(key='condition', path='Condition'),
        XmlField(key='price', path='Price', cast=float, default='0'),
        XmlField(key='meter', path='Meter', cast=float, default='0'),
        XmlField(key='meter_unit', path='MeterUnit'),
        XmlField(key='misc_1', path='Misc1'),
        XmlField(key='misc_2', path='Misc2'),
        XmlField(key='public_comment', path='PublicComment'),
        XmlField(key='location_name', path='Location/Name'),
        XmlField(key='location_city', path='Location/City'),
        XmlField(key='location_state_code', path='Location/StateCode'),
        XmlField(key='location_zip_code', path='Location/ZipCode'),
        XmlField(key='location_phone', path='Location/Phone'),
        XmlListField(key='images', path='Images/Image'),
    ],
)


class MemoryStorage:
    def __init__(self, identity_field: str = 'stock_number') -> None:
        self._identity_field = identity_field
        self.records: dict[str, dict[str, Any]] = {}
        self.hashes: dict[str, str] = {}

    def create_many(self, records: list[dict[str, Any]], hashes: dict[str, str]) -> None:
        for record in records:
            key = str(record[self._identity_field])
            self.records[key] = record

        self.hashes.update(hashes)

    def deactivate_many(self, keys: set[str]) -> None:
        for key in keys:
            del self.records[key]
            self.hashes.pop(key, None)

    def get_active_keys(self) -> set[str]:
        return set(self.records)

    def get_hashes(self, keys: set[str]) -> dict[str, str]:
        return {k: v for k, v in self.hashes.items() if k in keys}

    def get_many(self, keys: set[str]) -> dict[str, dict[str, Any]]:
        return {k: dict(v) for k, v in self.records.items() if k in keys}

    def update_many(self, records: list[dict[str, Any]], hashes: dict[str, str]) -> None:
        for record in records:
            key = str(record[self._identity_field])
            self.records[key] = record

        self.hashes.update(hashes)


@pytest.fixture
def storage() -> MemoryStorage:
    return MemoryStorage()


@pytest.fixture
def engine(storage: MemoryStorage) -> Engine:
    return Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=None,
    )


def test_initial_sync_creates_all(engine: Engine, storage: MemoryStorage) -> None:
    result = engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert len(result.created) == 2
    assert result.updated == []
    assert result.deactivated == []
    assert '13511' in storage.records
    assert '16992' in storage.records


def test_unchanged_units_not_updated(engine: Engine) -> None:
    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)
    result = engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert result.created == []
    assert result.updated == []
    assert len(result.unchanged) == 2


def test_missing_unit_deactivated(engine: Engine, storage: MemoryStorage) -> None:
    storage.records['GONE'] = {'stock_number': 'GONE'}
    storage.hashes['GONE'] = 'stale'

    result = engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert 'GONE' in result.deactivated
    assert 'GONE' not in storage.records
    assert 'GONE' not in storage.hashes


def test_changed_unit_updated(engine: Engine, storage: MemoryStorage) -> None:
    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    storage.records['13511']['price'] = 999.99
    storage.hashes['13511'] = 'stale'

    result = engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert '13511' in result.updated
    assert storage.records['13511']['price'] == 226900.00


def test_empty_xml_deactivates_all(engine: Engine, storage: MemoryStorage) -> None:
    storage.records['13511'] = {'stock_number': '13511'}
    storage.hashes['13511'] = 'stale'

    result = engine.sync(FIXTURES_DIR / 'empty_units.xml', parser=UNIT_PARSER)

    assert '13511' in result.deactivated
    assert '13511' not in storage.records
    assert result.created == []


def test_on_created_callback(storage: MemoryStorage) -> None:
    created_records: dict[str, Any] = {}

    def on_created(key: str, record: dict[str, Any]) -> None:
        created_records[key] = record

    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=None,
        on_created=on_created,
    )

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert '13511' in created_records
    assert '16992' in created_records


def test_on_updated_callback(storage: MemoryStorage) -> None:
    updated_records: dict[str, Any] = {}

    def on_updated(key: str, old: dict[str, Any], new: dict[str, Any]) -> None:
        updated_records[key] = (old, new)

    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=None,
        on_updated=on_updated,
    )

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)
    storage.records['16992']['manufacturer'] = 'Changed'
    storage.hashes['16992'] = 'stale'

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert '16992' in updated_records
    assert updated_records['16992'][0]['manufacturer'] == 'Changed'
    assert updated_records['16992'][1]['manufacturer'] == 'Hyundai'


def test_on_deactivated_callback(storage: MemoryStorage) -> None:
    deactivated_keys: list[str] = []

    def on_deactivated(key: str) -> None:
        deactivated_keys.append(key)

    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=None,
        on_deactivated=on_deactivated,
    )

    storage.records['GONE'] = {'stock_number': 'GONE'}
    storage.hashes['GONE'] = 'stale'

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert 'GONE' in deactivated_keys


def test_missing_fields_unit_syncs(engine: Engine, storage: MemoryStorage) -> None:
    result = engine.sync(FIXTURES_DIR / 'missing_fields_units.xml', parser=UNIT_PARSER)

    assert '99999' in result.created
    assert storage.records['99999']['year'] == 0
    assert storage.records['99999']['manufacturer'] == ''


def test_sync_records_without_file() -> None:
    id_storage = MemoryStorage(identity_field='id')

    engine = Engine(
        storage=id_storage,
        identity_field='id',
        deactivation_threshold=None,
    )

    records = [
        {'id': '1', 'name': 'Alpha'},
        {'id': '2', 'name': 'Beta'},
    ]

    result = engine.sync_records(records)

    assert len(result.created) == 2
    assert '1' in id_storage.records
    assert '2' in id_storage.records


def test_compare_fields_limits_detection(storage: MemoryStorage) -> None:
    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=None,
        compare_fields=['price'],
    )

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)
    storage.records['13511']['manufacturer'] = 'Changed'

    result = engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert '13511' not in result.updated
    assert '13511' in result.unchanged


def test_duplicate_identity_reports_error() -> None:
    id_storage = MemoryStorage(identity_field='id')

    engine = Engine(
        storage=id_storage,
        identity_field='id',
        deactivation_threshold=None,
    )

    records = [
        {'id': '1', 'name': 'First'},
        {'id': '1', 'name': 'Duplicate'},
    ]

    result = engine.sync_records(records)

    assert len(result.created) == 1
    assert len(result.errors) == 1
    assert result.errors[0].key == '1'


def test_hashes_stored_on_create(engine: Engine, storage: MemoryStorage) -> None:
    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert '13511' in storage.hashes
    assert '16992' in storage.hashes
    assert ':' in storage.hashes['13511']

    tag, body = storage.hashes['13511'].split(':', 1)

    assert len(tag) == 8
    assert len(body) == 64


def test_hashes_updated_on_change(engine: Engine, storage: MemoryStorage) -> None:
    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    original_hash = storage.hashes['13511']
    storage.records['13511']['price'] = 999.99
    storage.hashes['13511'] = 'stale'

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert storage.hashes['13511'] == original_hash
    assert storage.hashes['13511'] != 'stale'


def test_unchanged_skips_get_many() -> None:
    get_many_calls: list[set[str]] = []

    class TrackingStorage(MemoryStorage):
        def get_many(self, keys: set[str]) -> dict[str, dict[str, Any]]:
            get_many_calls.append(keys)
            return super().get_many(keys)

    tracking = TrackingStorage()

    engine = Engine(
        storage=tracking,
        identity_field='stock_number',
        deactivation_threshold=None,
    )

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)
    get_many_calls.clear()

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert get_many_calls == []


def test_get_many_only_for_updated_with_callback() -> None:
    get_many_calls: list[set[str]] = []

    class TrackingStorage(MemoryStorage):
        def get_many(self, keys: set[str]) -> dict[str, dict[str, Any]]:
            get_many_calls.append(keys)
            return super().get_many(keys)

    tracking = TrackingStorage()

    def on_updated(key: str, old: dict[str, Any], new: dict[str, Any]) -> None:
        pass

    engine = Engine(
        storage=tracking,
        identity_field='stock_number',
        deactivation_threshold=None,
        on_updated=on_updated,
    )

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)
    get_many_calls.clear()

    tracking.records['13511']['price'] = 999.99
    tracking.hashes['13511'] = 'stale'

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert len(get_many_calls) == 1
    assert get_many_calls[0] == {'13511'}


def test_callbacks_fire_after_mutations() -> None:
    call_order: list[str] = []

    class TrackingStorage(MemoryStorage):
        def create_many(self, records: list[dict[str, Any]], hashes: dict[str, str]) -> None:
            call_order.append('create_many')
            super().create_many(records, hashes)

    tracking = TrackingStorage()

    def on_created(key: str, _record: dict[str, Any]) -> None:
        call_order.append(f'callback:{key}')

    engine = Engine(
        storage=tracking,
        identity_field='stock_number',
        deactivation_threshold=None,
        on_created=on_created,
    )

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert call_order[0] == 'create_many'
    assert all(c.startswith('callback:') for c in call_order[1:])


def test_dry_run_no_mutations(engine: Engine, storage: MemoryStorage) -> None:
    result = engine.sync(
        FIXTURES_DIR / 'sample_units.xml',
        parser=UNIT_PARSER,
        dry_run=True,
    )

    assert len(result.created) == 2
    assert storage.records == {}
    assert storage.hashes == {}


def test_dry_run_reports_deactivations(engine: Engine, storage: MemoryStorage) -> None:
    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    storage.records['GONE'] = {'stock_number': 'GONE'}
    storage.hashes['GONE'] = 'stale'

    result = engine.sync(
        FIXTURES_DIR / 'sample_units.xml',
        parser=UNIT_PARSER,
        dry_run=True,
    )

    assert 'GONE' in result.deactivated
    assert 'GONE' in storage.records


def test_dry_run_reports_updates(engine: Engine, storage: MemoryStorage) -> None:
    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    storage.records['13511']['price'] = 999.99
    storage.hashes['13511'] = 'stale'

    result = engine.sync(
        FIXTURES_DIR / 'sample_units.xml',
        parser=UNIT_PARSER,
        dry_run=True,
    )

    assert '13511' in result.updated
    assert storage.records['13511']['price'] == 999.99


def test_missing_hash_treated_as_changed(engine: Engine, storage: MemoryStorage) -> None:
    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)
    del storage.hashes['13511']

    result = engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert '13511' in result.updated


def test_none_identity_rejected() -> None:
    id_storage = MemoryStorage(identity_field='id')

    engine = Engine(
        storage=id_storage,
        identity_field='id',
        deactivation_threshold=None,
    )

    records = [
        {'id': None, 'name': 'Ghost'},
        {'id': '1', 'name': 'Valid'},
    ]

    result = engine.sync_records(records)

    assert len(result.created) == 1
    assert len(result.errors) == 1
    assert '1' in id_storage.records


def test_callback_error_collected_not_raised(storage: MemoryStorage) -> None:
    def on_created(_key: str, _record: dict[str, Any]) -> None:
        msg = 'boom'
        raise RuntimeError(msg)

    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=None,
        on_created=on_created,
    )

    result = engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert len(result.created) == 2
    assert len(result.errors) == 2
    assert '13511' in storage.records
    assert '16992' in storage.records

    assert all(e.exception is not None for e in result.errors)


def test_callback_error_does_not_skip_remaining(storage: MemoryStorage) -> None:
    called: list[str] = []

    def on_created(key: str, _record: dict[str, Any]) -> None:
        if key == '13511':
            msg = 'fail'
            raise RuntimeError(msg)
        called.append(key)

    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=None,
        on_created=on_created,
    )

    result = engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert '16992' in called
    assert len(result.errors) == 1


def test_deactivation_threshold_aborts() -> None:
    storage = MemoryStorage()

    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=0.5,
    )

    for i in range(10):
        key = str(i)
        storage.records[key] = {'stock_number': key}
        storage.hashes[key] = f'hash-{key}'

    records = [{'stock_number': '0'}, {'stock_number': '1'}]

    with pytest.raises(SyncAbortedError, match='exceeds threshold'):
        engine.sync_records(records)

    assert len(storage.records) == 10


def test_deactivation_threshold_allows_within_limit() -> None:
    storage = MemoryStorage()

    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=0.5,
    )

    for i in range(10):
        key = str(i)
        storage.records[key] = {'stock_number': key}
        storage.hashes[key] = f'hash-{key}'

    records = [{'stock_number': str(i)} for i in range(6)]

    result = engine.sync_records(records)

    assert len(result.deactivated) == 4
    assert len(storage.records) == 6


def test_deactivation_threshold_disabled() -> None:
    storage = MemoryStorage()

    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=None,
    )

    for i in range(10):
        key = str(i)
        storage.records[key] = {'stock_number': key}
        storage.hashes[key] = f'hash-{key}'

    result = engine.sync_records([])

    assert len(result.deactivated) == 10
    assert len(storage.records) == 0


def test_transaction_wraps_mutations(storage: MemoryStorage) -> None:
    entered = []

    @contextmanager
    def fake_transaction() -> Iterator[None]:
        entered.append(True)
        yield

    engine = Engine(
        storage=storage,
        identity_field='stock_number',
        deactivation_threshold=None,
        transaction=fake_transaction,
    )

    engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert len(entered) == 1


def test_transaction_rollback_on_storage_failure() -> None:
    mutations: list[str] = []
    rolled_back: list[bool] = []

    class FailingStorage(MemoryStorage):
        def create_many(self, records: list[dict[str, Any]], hashes: dict[str, str]) -> None:
            mutations.append('create')
            super().create_many(records, hashes)

        def update_many(self, _records: list[dict[str, Any]], _hashes: dict[str, str]) -> None:
            msg = 'storage exploded'
            raise RuntimeError(msg)

    @contextmanager
    def fake_atomic() -> Iterator[None]:
        try:
            yield
        except Exception:
            rolled_back.append(True)
            raise

    failing = FailingStorage()
    failing.records['13511'] = {'stock_number': '13511'}
    failing.hashes['13511'] = 'stale'

    engine = Engine(
        storage=failing,
        identity_field='stock_number',
        deactivation_threshold=None,
        transaction=fake_atomic,
    )

    with pytest.raises(RuntimeError, match='storage exploded'):
        engine.sync(FIXTURES_DIR / 'sample_units.xml', parser=UNIT_PARSER)

    assert len(rolled_back) == 1
