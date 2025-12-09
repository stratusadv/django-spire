from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.seeding.field.base import BaseFieldSeeder

if TYPE_CHECKING:
    from typing_extensions import Any


class StaticFieldSeeder(BaseFieldSeeder):
    keyword = 'static'

    def seed(self, manager: Any = None, count: int = 1) -> list[dict]:
        return [
            {field_name: value[1] for field_name, value in self.seeder_fields.items()}
            for _ in range(count)
        ]
