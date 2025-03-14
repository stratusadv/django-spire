from django.urls import path

from testing.dummy import views


app_name = 'dummy'

urlpatterns = [
    path('home',
        views.home,
        name='home'),
]
