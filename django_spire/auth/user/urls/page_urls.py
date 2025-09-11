from django.urls import path

from django_spire.auth.user.views import page_views

app_name = 'page'

urlpatterns = [
    path('user/<int:pk>/detail/', page_views.detail_view, name='detail'),
    path('user/list/', page_views.list_view, name='list'),
]
