from django.urls import path

from django_spire.home import views

app_name = 'home'

urlpatterns = [
    path('', views.home_view, name='home'),

    # Path has to match Maintenance Mode Middleware
    path('maintenance/mode', views.maintenance_mode_view, name='maintenance_mode'),
]
