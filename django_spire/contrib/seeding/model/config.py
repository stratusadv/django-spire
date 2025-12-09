from __future__ import annotations

from typing import TYPE_CHECKING

from django_spire.contrib.seeding.field.cleaners import normalize_seeder_fields
from django_spire.contrib.seeding.model.enums import ModelSeederDefaultsEnum

if TYPE_CHECKING:
    from typing_extensions import Any, Self


class FieldsConfig:
    def __init__(
        self,
        raw_fields: dict[str, Any],
        field_names: list[str],
        default_to: str,
        model_class: Any
    ) -> None:
        self.raw_fields = raw_fields or {}
        self.default_to = default_to
        self.field_names = set(field_names)
        self.model_class = model_class

        self._excluded = {
            k for k, v in self.raw_fields.items()
            if v in ("exclude", ("exclude",))
        }

        self.fields = normalize_seeder_fields({
            k: v for k, v in self.raw_fields.items() if k not in self._excluded
        })

        self._validate()
        self._assign_defaults()

        # Fields need to be in order for caching hash
        self._order_fields()

    def _validate(self) -> None:
        unknown = set(self.fields.keys()) - self.field_names

        if unknown:
            message = f"Invalid field name(s): {', '.join(unknown)}"
            raise ValueError(message)

    def _assign_defaults(self) -> None:
        if self.default_to == ModelSeederDefaultsEnum.INCLUDED:
            return

        method = self.default_to.lower()

        for name in self.field_names:
            if name not in self.fields and name not in self._excluded:
                self.fields[name] = (method,)

    def override(self, overrides: dict) -> Self:
        merged = {**self.fields, **normalize_seeder_fields(overrides)}
        new_raw = {
            **{k: v for k, v in self.raw_fields.items() if k in self._excluded},
            **merged
        }
        return self.__class__(
            raw_fields=new_raw,
            field_names=list(self.field_names),
            default_to=self.default_to,
            model_class=self.model_class
        )

    def _order_fields(self) -> None:
        self.fields = dict(
            sorted(
                self.fields.items(),
                key=lambda x: x[0]
            )
        )

    @property
    def excluded(self) -> set:
        return self._excluded
