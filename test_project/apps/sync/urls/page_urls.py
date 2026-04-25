from __future__ import annotations

from django.urls import path

from test_project.apps.sync.views import page_views


app_name = 'page'

urlpatterns = [
    path('dashboard/', page_views.dashboard_page_view, name='dashboard'),
    path('switch/<str:db_name>/', page_views.switch_db_view, name='switch_db'),
    path('list/<str:model>/', page_views.list_page_view, name='list'),
    path('verification/', page_views.verification_page_view, name='verification'),
    path('<str:model>/<int:pk>/detail/', page_views.detail_page_view, name='detail'),
]
