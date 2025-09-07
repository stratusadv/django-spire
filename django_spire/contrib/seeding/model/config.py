from django_spire.contrib.seeding.field.cleaners import normalize_seeder_fields
from django_spire.contrib.seeding.model.enums import ModelSeederDefaultsEnum


class FieldsConfig:
    def __init__(
            self,
            raw_fields: dict,
            field_names: list[str],
            default_to: str,
            model_class
    ):
        self.raw_fields = raw_fields or {}
        self.default_to = default_to
        self.field_names = set(field_names)
        self.model_class = model_class

        self._excluded = {
            k for k, v in self.raw_fields.items()
            if v == "exclude" or v == ("exclude",)
        }

        self.fields = normalize_seeder_fields({
            k: v for k, v in self.raw_fields.items() if k not in self._excluded
        })

        self._validate()
        self._assign_defaults()
        self._order_fields() # Fields need to be in order for caching hash

    def _validate(self):
        unknown = set(self.fields.keys()) - self.field_names
        if unknown:
            raise ValueError(f"Invalid field name(s): {', '.join(unknown)}")

    def _assign_defaults(self):
        if self.default_to == ModelSeederDefaultsEnum.INCLUDED:
            return

        method = self.default_to.lower()

        for name in self.field_names:
            if name not in self.fields and name not in self._excluded:
                self.fields[name] = (method,)

    def override(self, overrides: dict):
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

    def _order_fields(self):
        self.fields = {k: v for k, v in sorted(self.fields.items(), key=lambda x: x[0])}

    @property
    def excluded(self):
        return self._excluded
