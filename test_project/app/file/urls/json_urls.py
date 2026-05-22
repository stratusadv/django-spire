from django.urls import path

from test_project.apps.file.views import json_views


app_name = 'json'

urlpatterns = [
    path('<int:pk>/attachment/add/', json_views.add_attachment_view, name='add_attachment'),
    path('<int:pk>/attachments/add/', json_views.add_attachments_view, name='add_attachments'),
    path('<int:pk>/attachment/add-validated/', json_views.add_validated_attachment_view, name='add_validated_attachment'),
    path('<int:pk>/attachment/<int:file_pk>/delete/', json_views.delete_attachment_view, name='delete_attachment'),
    path('<int:pk>/attachments/delete/', json_views.delete_attachments_view, name='delete_attachments'),
    path('<int:pk>/attachments/replace/', json_views.replace_attachments_view, name='replace_attachments'),
    path('<int:pk>/profile-picture/delete/', json_views.delete_profile_picture_view, name='delete_profile_picture'),
    path('<int:pk>/profile-picture/replace/', json_views.replace_profile_picture_view, name='replace_profile_picture'),
]
