from django.urls import path

from test_project.apps.tabular.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_page, name='list'),
    path('migration-list/', page_views.migration_list_page, name='migration_list'),
]
