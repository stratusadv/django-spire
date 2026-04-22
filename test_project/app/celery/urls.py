from django.urls import path, include

from test_project.apps.celery import views


app_name = 'celery'

urlpatterns = [
    path('home/', views.celery_home_view, name='home'),
]
