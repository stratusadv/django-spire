from django.urls import path

from django_spire.help_desk.views import page_views

app_name = 'page'

urlpatterns = [
    path('list/', page_views.ticket_list_view, name='list'),
    path('<int:pk>/detail/', page_views.ticket_detail_view, name='detail'),
]
