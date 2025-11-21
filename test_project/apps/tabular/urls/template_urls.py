from django.urls import path

from test_project.apps.tabular.views import template_views


app_name = 'template'

urlpatterns = [
    path('migration/rows/', template_views.migration_rows_view, name='migration_rows'),
    path('<int:task_id>/detail/rows/', template_views.detail_rows_view, name='detail_rows'),
    path('<int:task_id>/user/rows/', template_views.user_rows_view, name='user_rows'),
    path('rows/', template_views.rows_view, name='rows'),
    path('user/<int:user_id>/task/detail/rows/', template_views.user_detail_rows_view, name='user_detail_rows'),
]
