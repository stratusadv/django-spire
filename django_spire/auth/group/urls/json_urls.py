from __future__ import annotations

from django.urls import path

from django_spire.auth.group.views import json_views


app_name = 'group'

# Group
urlpatterns = [
    path('group/<int:pk>/permission/<str:app_name>/ajax/',
         json_views.permission_form_ajax,
         name='group_permission_ajax'),

    path('group/<int:pk>/app/<str:app_name>/special/role/ajax/',
         json_views.special_role_form_ajax,
         name='group_special_role_ajax'),
]
