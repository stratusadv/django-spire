from django.urls import path

from test_project.apps.tabular import views


app_name = 'tabular'

urlpatterns = [
    path('', views.tabular_home_view, name='home'),
]
