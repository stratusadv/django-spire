from django.urls import path

from test_project.apps.tabular.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_page, name='list'),
    path('migration-table/', page_views.migration_table_page, name='migration_table'),
    path('table/', page_views.table_page, name='table')
]
