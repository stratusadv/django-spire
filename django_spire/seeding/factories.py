from pydantic.fields import Field


class SeedIntelFieldFactory:

    def __init__(self, model_field: Field):
        self.model_field = model_field

    def build_field(self) -> Field:
        kwargs = {
            'description': '',
        }

        if self.model_field.null:
            kwargs['default'] = None

        if self.model_field.get_internal_type() in ['DateField']:
            kwargs['description'] += 'Date Format: YYYY-MM-DD '
            kwargs['examples'] = ['2022-01-01']

        if self.model_field.get_internal_type() in ['DateTimeField']:
            kwargs['description'] += 'Date Format: YYYY-MM-DD HH:MM:SS '
            kwargs['examples'] = ['2022-01-01 13:37:00']

        if self.model_field.unique:
            kwargs['description'] += 'Is Unique: True '

        if self.model_field.get_internal_type() in ['CharField', 'TextField'] and self.model_field.max_length:
            kwargs['max_length'] = int(self.model_field.max_length)

        return Field(**kwargs)
