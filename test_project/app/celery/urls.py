from django.urls import path

from test_project.app.celery import views


app_name = 'celery'

urlpatterns = [
    path('home/', views.celery_home_view, name='home'),
    path('help_modal/', views.celery_help_modal_view, name='help_modal')
]
