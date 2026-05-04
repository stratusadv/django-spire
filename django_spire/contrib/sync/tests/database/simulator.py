from __future__ import annotations

import random

from enum import Enum, auto
from typing import Any

from django_spire.contrib.sync.database.record import SyncRecord
from django_spire.contrib.sync.tests.database.harness import ModelSchema, MultiTabletHarness
from django_spire.contrib.sync.tests.database.oracle import SyncOracle


class OpTag(Enum):
    WRITE_TABLET = auto()
    WRITE_SERVER = auto()
    SYNC_TABLET = auto()
    SYNC_ALL = auto()
    CRASH_MID_SYNC = auto()


class SyncSimulator:
    def __init__(
        self,
        tablet_count: int = 2,
        schemas: list[ModelSchema] | None = None,
        num_keys: int = 5,
        seed: int | None = None,
    ) -> None:
        self.rng = random.Random(seed)
        self.num_keys = num_keys

        self.harness = MultiTabletHarness(
            tablet_count=tablet_count,
            schemas=schemas,
            seed=seed,
        )

        self.oracle = SyncOracle()
        self._snapshots: dict[str, dict] = {}
        self._weights = self._generate_weights()

    @property
    def tablet_ids(self) -> list[str]:
        return self.harness.tablet_ids

    @property
    def model_labels(self) -> list[str]:
        return self.harness.model_labels

    def _generate_weights(self) -> dict[OpTag, int]:
        return {
            OpTag.WRITE_TABLET: self.rng.randint(10, 100),
            OpTag.WRITE_SERVER: self.rng.randint(0, 50),
            OpTag.SYNC_TABLET: self.rng.randint(5, 30),
            OpTag.SYNC_ALL: self.rng.randint(0, 10),
            OpTag.CRASH_MID_SYNC: self.rng.randint(0, 5) if self.rng.random() < 0.5 else 0,
        }

    def _pick_op(self) -> OpTag:
        total = sum(self._weights.values())
        if total == 0:
            return OpTag.WRITE_TABLET

        roll = self.rng.randint(1, total)
        cumulative = 0
        for op, weight in self._weights.items():
            cumulative += weight
            if roll <= cumulative:
                return op
        return OpTag.WRITE_TABLET

    def _generate_fields(
        self,
        model_label: str,
        key: str,
    ) -> tuple[dict[str, Any], dict[str, int]]:
        ts = self.harness.ts()
        schema = self.harness.schemas[model_label]

        fields_to_update = self.rng.sample(
            schema.fields,
            k=self.rng.randint(1, len(schema.fields)),
        )

        data: dict[str, Any] = {'id': key}
        timestamps: dict[str, int] = {}

        for field_name in fields_to_update:
            data[field_name] = self.harness._random_value(field_name)
            timestamps[field_name] = ts

        return data, timestamps

    def _merge_into_existing(
        self,
        storage: Any,
        model_label: str,
        key: str,
        data: dict[str, Any],
        timestamps: dict[str, int],
    ) -> tuple[dict[str, Any], dict[str, int]]:
        existing = storage._records[model_label].get(key)
        if existing is not None:
            return {**existing.data, **data}, {**existing.timestamps, **timestamps}
        return data, timestamps

    def write_tablet(
        self,
        tablet_id: str,
        model_label: str,
        key: str,
    ) -> None:
        data, timestamps = self._generate_fields(model_label, key)
        storage = self.harness.tablet_storages[tablet_id]
        data, timestamps = self._merge_into_existing(
            storage, model_label, key, data, timestamps,
        )
        self.harness.tablet_save(tablet_id, model_label, key, data, timestamps)
        self.oracle.record_write(model_label, key, data, timestamps)

    def write_server(self, model_label: str, key: str) -> None:
        data, timestamps = self._generate_fields(model_label, key)
        storage = self.harness.server_storage
        data, timestamps = self._merge_into_existing(
            storage, model_label, key, data, timestamps,
        )
        self.harness.server_save(model_label, key, data, timestamps)
        self.oracle.record_write(model_label, key, data, timestamps)

    def snapshot_tablet(self, tablet_id: str) -> None:
        storage = self.harness.tablet_storages[tablet_id]
        self._snapshots[tablet_id] = {
            'records': {
                model: {
                    k: SyncRecord(
                        key=rec.key,
                        data=dict(rec.data),
                        timestamps=dict(rec.timestamps),
                    )
                    for k, rec in records.items()
                }
                for model, records in storage._records.items()
            },
            'checkpoints': dict(storage._checkpoints),
        }

    def restore_tablet(self, tablet_id: str) -> None:
        snapshot = self._snapshots.pop(tablet_id)
        storage = self.harness.tablet_storages[tablet_id]
        storage._records = snapshot['records']
        storage._checkpoints = snapshot['checkpoints']

    def crash_mid_sync(self, tablet_id: str) -> None:
        self.snapshot_tablet(tablet_id)
        self.harness.sync_tablet(tablet_id)
        self.restore_tablet(tablet_id)

    def run(self, num_operations: int, converge: bool = True) -> None:
        keys = [f'k-{i}' for i in range(self.num_keys)]

        for _ in range(num_operations):
            op = self._pick_op()
            model_label = self.rng.choice(self.model_labels)

            if op == OpTag.WRITE_TABLET:
                tablet_id = self.rng.choice(self.tablet_ids)
                self.write_tablet(tablet_id, model_label, self.rng.choice(keys))

            elif op == OpTag.WRITE_SERVER:
                self.write_server(model_label, self.rng.choice(keys))

            elif op == OpTag.SYNC_TABLET:
                self.harness.sync_tablet(self.rng.choice(self.tablet_ids))

            elif op == OpTag.SYNC_ALL:
                self.harness.sync_all()

            elif op == OpTag.CRASH_MID_SYNC:
                self.crash_mid_sync(self.rng.choice(self.tablet_ids))

        if converge:
            self.harness.sync_all_converge(rounds=3)

    def assert_converged_with_oracle(self) -> None:
        for model_label in self.model_labels:
            expected_keys = self.oracle.expected_keys(model_label)
            server_keys = set(
                self.harness.server_storage._records[model_label].keys()
            )

            assert expected_keys == server_keys, (
                f'{model_label} key mismatch: '
                f'oracle_only={expected_keys - server_keys} '
                f'server_only={server_keys - expected_keys}'
            )

            for key in expected_keys:
                expected = self.oracle.expected_data(model_label, key)
                server_rec = self.harness.server_record(model_label, key)

                assert server_rec is not None, (
                    f'{model_label}:{key} missing from server'
                )

                for field, expected_value in expected.items():
                    actual_value = server_rec.data.get(field)
                    assert actual_value == expected_value, (
                        f'{model_label}:{key}.{field} mismatch: '
                        f'oracle={expected_value} server={actual_value}'
                    )

        self.harness.assert_converged()
