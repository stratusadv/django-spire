from django.urls import path

from module.views import page_views

app_name = 'page'
urlpatterns = [
    path('', page_views.home_page, name='home'),
]