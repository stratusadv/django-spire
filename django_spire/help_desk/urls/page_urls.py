from __future__ import annotations

from django.urls import path

from django_spire.help_desk.views import page_views


app_name = 'page'

urlpatterns = [
    path('detail/<int:pk>/', page_views.ticket_detail_view, name='detail'),
    path('list/', page_views.ticket_list_view, name='list'),
]
