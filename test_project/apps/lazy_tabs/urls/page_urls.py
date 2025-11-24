from django.urls import path

from test_project.apps.lazy_tabs.views import page_views


app_name = 'page'

urlpatterns = [
    path('demo/', page_views.demo_page_view, name='demo'),
]
