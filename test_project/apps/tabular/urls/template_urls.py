from django.urls import path

from test_project.apps.tabular.views import template_views


app_name = 'template'

urlpatterns = [
    path('api/migration/rows/', template_views.migration_rows_view, name='migration_rows'),
    path('api/task/<int:task_id>/detail/rows/', template_views.task_detail_rows_view, name='task_detail_rows'),
    path('api/task/<int:task_id>/user/rows/', template_views.task_user_rows_view, name='task_user_rows'),
    path('api/task/rows/', template_views.task_rows_view, name='task_rows'),
    path('api/user/<int:user_id>/task/detail/rows/', template_views.task_user_detail_rows_view, name='task_user_detail_rows'),
]
