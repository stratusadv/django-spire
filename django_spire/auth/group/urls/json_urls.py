from django.urls import path

from django_spire.auth.group.views import json_views


app_name = 'json'

urlpatterns = [
    path('<int:pk>/app/<str:app_name>/update/',
         json_views.group_update_permission_json,
         name='update_permission'),
    path('<int:pk>/app/<str:app_name>/add_special_role/',
         json_views.group_add_special_role,
         name='add_special_role'),
]