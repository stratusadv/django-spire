from django.conf import settings as django_settings

from django_spire import settings as django_spire_default_settings


class Settings:
    def __getattr__(self, name: str):
        django_value = None
        django_spire_value = None

        if hasattr(django_settings, name):
            django_value = getattr(django_settings, name)

        if hasattr(django_spire_default_settings, name):
            django_spire_value = getattr(django_spire_default_settings, name)

        if name == 'DJANGO_SPIRE_AUTH_CONTROLLERS':
            if isinstance(django_value, dict) and isinstance(django_spire_value, dict):
                return {
                    **django_spire_value,
                    **django_value
                }

        if django_value is not None:
            return django_value

        if django_spire_value is not None:
            return django_spire_value

        return None

settings = Settings()
