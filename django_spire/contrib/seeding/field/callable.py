from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.seeding.field.base import BaseFieldSeeder
from django_spire.contrib.seeding.field.enums import FieldSeederTypesEnum

if TYPE_CHECKING:
    from typing_extensions import Any


class CallableFieldSeeder(BaseFieldSeeder):
    keyword = FieldSeederTypesEnum.CALLABLE

    def seed(self, manager: Any = None, count: int = 1) -> list[dict]:
        return [
            {field_name: func[1]() for field_name, func in self.seeder_fields.items()}
            for _ in range(count)
        ]
