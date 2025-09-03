from django.urls import path

from test_project.apps.ordering.views import page_views


app_name = 'page'

urlpatterns = [
    path('demo/', page_views.demo_view, name='demo'),
]
