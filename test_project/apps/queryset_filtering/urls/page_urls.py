from django.urls import path

from test_project.apps.queryset_filtering.views import page_views


app_name = 'page'

urlpatterns = [
    path('list/', page_views.list_page, name='list'),
]
