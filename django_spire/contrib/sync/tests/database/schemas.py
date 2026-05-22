from __future__ import annotations

from django_spire.contrib.sync.tests.database.harness import ModelSchema


FLAT_SCHEMA = [
    ModelSchema(label='app.Record', fields=['name', 'value', 'is_active']),
]

HIERARCHICAL_SCHEMA = [
    ModelSchema(label='app.Parent', fields=['name', 'value']),
    ModelSchema(
        label='app.Child',
        fields=['x', 'y', 'is_active'],
        dependencies={'app.Parent'},
    ),
]

WIDE_SCHEMA = [
    ModelSchema(
        label='app.Wide',
        fields=[f'field_{i}' for i in range(20)],
    ),
]
