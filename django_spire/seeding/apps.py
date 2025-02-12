from django.apps import AppConfig


class SeedingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'spire_seeding'
    name = 'django_spire.seeding'
