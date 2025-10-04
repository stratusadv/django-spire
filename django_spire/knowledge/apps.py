from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class KnowledgeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_knowledge'
    name = 'django_spire.knowledge'
    MODEL_PERMISSIONS = (
        {
            'name': 'knowledge',
            'verbose_name': 'Knowledge',
            'model_class_path': 'django_spire.knowledge.collection.models.Collection',
            'is_proxy_model': False,
        },
    )

    REQUIRED_APPS = ('django_spire_core',)

    URLPATTERNS_INCLUDE = 'django_spire.knowledge.urls'
    URLPATTERNS_NAMESPACE = 'knowledge'

    def ready(self) -> None:
        check_required_apps(self.label)
