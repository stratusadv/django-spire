from django.urls import path

from example.tabular import views


app_name = 'tabular'

urlpatterns = [
    path('', views.tabular_home_view, name='home'),
]
