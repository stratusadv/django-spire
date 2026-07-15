from django.db.models import ForeignKey

from django_spire.contrib.seeder.seed.factory.base import BaseSeedFactory


class ModelSeedFactory(BaseSeedFactory):
    @property
    def _model_used_field_names(self) -> set[str]:
        return {
            f.attname if isinstance(f, ForeignKey) else f.name
            for f in self.seeder.model_class._meta.fields
        }

    @property
    def _model_all_field_names(self) -> set[str]:
        field_names = self._model_used_field_names
        field_names.update(f.attname for f in self.seeder.model_class._meta.fields)
        return field_names

    def _validate(self) -> None:
        invalid_field_names = set(self.seeder.fields_seeds.keys()) - self._model_all_field_names

        if invalid_field_names:
            message = f'Invalid field name(s): {", ".join(invalid_field_names)}'
            raise ValueError(message)
