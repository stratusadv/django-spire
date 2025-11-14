from django.urls import path

from test_project.apps.tabular.views import template_views


app_name = 'template'

urlpatterns = [
    path('api/rows/', template_views.tabular_rows_view, name='rows'),
    path('api/<int:task_id>/children/', template_views.tabular_child_rows_view, name='child_rows'),
    path('api/user/<int:user_id>/details/', template_views.user_details_view, name='user_details'),
]
