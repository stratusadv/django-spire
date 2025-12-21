from __future__ import annotations

from django.apps import AppConfig

from django_spire.utils import check_required_apps


class CommentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'django_spire_comment'
    name = 'django_spire.comment'

    REQUIRED_APPS = ('django_spire_core',)
    URLPATTERNS_INCLUDE = 'django_spire.comment.urls'
    URLPATTERNS_NAMESPACE = 'comment'

    def ready(self) -> None:
        check_required_apps(self.label)
