from django.urls import path

from test_project.apps.home.views import page_views


app_name = 'page'

urlpatterns = [
    path('', page_views.home_view, name='home'),
]
