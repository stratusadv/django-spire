from django.urls import path

from django_spire.help_desk.views import page_views


app_name = 'help_desk'

urlpatterns = [
    path('', page_views.ticket_list_view, name='home'),
]