from django.urls import path

from test_project.apps.theme.views import page_views

app_name = 'page'
urlpatterns = [
    path('dashboard/', page_views.dashboard_view, name='dashboard'),
]
