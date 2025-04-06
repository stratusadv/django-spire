from django.db.models.fields.related import ForeignKey

from django_spire.seeding.model.config import FieldsConfig


class DjangoModelFieldsConfig(FieldsConfig):

    def _validate(self):
        valid_field_names = set(self.field_names)

        valid_field_names.update(f.attname for f in self.model_class._meta.fields)

        unknown = set(self.fields.keys()) - valid_field_names

        if unknown:
            raise ValueError(f"Invalid field name(s): {', '.join(unknown)}")

        # fk_fields = {
        #     f.name: f.attname  # f.attname = "user_id"
        #     for f in self.model_class._meta.fields
        #     if isinstance(f, ForeignKey)
        # }
        #
        # for name, value in self.fields.items():
        #     if name in fk_fields:
        #         valid_types = [int, None]
        #

    # def map_foreign_keys(self):
    #     fk_fields = {
    #         f.name: f.attname  # f.attname = "user_id"
    #         for f in self.model_class._meta.fields
    #         if isinstance(f, ForeignKey)
    #     }
    #
    #     # If asset_id and asset are passed, should I raise an error?
    #
    #     {
    #         'asset' : ('custom', 'in_order', {'values': [a.id for a in assets]}),
    #         'asset_id': ('custom', 'in_order', {'values': [a.id for a in assets]}),
    #     }
    #
    #     translated_fields = {}
    #     for name, value in self.fields.items():
    #         if name in fk_fields:
    #             translated_name = fk_fields[name]
    #
    #             if translated_name in self.field_names:
    #                 # Do not want to override asset_id if the user has already pass it in.
    #                 continue
    #             else:
    #                 translated_fields[translated_name] = value
    #         else:
    #             translated_fields[name] = value
    #
    #     return translated_fields
    #
    #     # Update self.fields.
    #
    #
