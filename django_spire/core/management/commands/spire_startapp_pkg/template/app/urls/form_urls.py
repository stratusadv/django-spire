from django.urls import path

from module.views import form_views

app_name = 'form'
urlpatterns = [
    path('', form_views.home_page, name='create'),
]