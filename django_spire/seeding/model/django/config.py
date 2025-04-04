from django.db.models.fields.related import ForeignKey

from django_spire.seeding.model.config import FieldsConfig


class DjangoModelFieldsConfig(FieldsConfig):

    def _validate(self):
        valid_field_names = set(self.field_names)

        valid_field_names.update(f.attname for f in self.model_class._meta.fields)

        unknown = set(self.fields.keys()) - valid_field_names
        if unknown:
            raise ValueError(f"Invalid field name(s): {', '.join(unknown)}")

    def _assign_defaults(self):
        super()._assign_defaults()

        if not self.model_class:
            return

        fk_fields = {
            f.name: f.attname  # f.attname = "user_id"
            for f in self.model_class._meta.fields
            if isinstance(f, ForeignKey)
        }

        translated_fields = {}
        for name, value in self.fields.items():
            if name in fk_fields:
                translated_name = fk_fields[name]
                translated_fields[translated_name] = value
            else:
                translated_fields[name] = value

        self.fields = translated_fields
