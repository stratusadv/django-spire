from django.urls import path

from django_spire.help_desk.views import page_views

app_name = 'page'

urlpatterns = [
    path('', page_views.list_view, name='list'),
]
