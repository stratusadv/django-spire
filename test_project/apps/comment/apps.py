from django.apps import AppConfig


class CommentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    label = 'test_project_comment'
    name = 'test_project.apps.comment'
