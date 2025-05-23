from django.urls import path

from django_spire.auth.group.views import page_views


app_name = 'page'

urlpatterns = [
    path('<int:pk>/detail/',
         page_views.group_detail_view,
         name='detail'),

    path('list/',
         page_views.group_list_view,
         name='list'),
]
