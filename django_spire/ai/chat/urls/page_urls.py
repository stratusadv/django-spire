from django.urls import path

from django_spire.ai.chat.views import page_views

app_name = 'page'

urlpatterns = [
    path('home/', page_views.home_view, name='home'),
]
