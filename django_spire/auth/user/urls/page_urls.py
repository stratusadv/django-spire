from django.urls import path

from django_spire.auth.user.views import page_views

app_name = 'page'

urlpatterns = [
    path('<int:pk>/detail/',
         page_views.user_detail_page_view,
         name='detail'),

    path('list/',
         page_views.user_list_page_view,
         name='list'),
]
