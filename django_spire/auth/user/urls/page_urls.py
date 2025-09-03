from django.urls import path

import django_spire.auth.user.views.form_views
from django_spire.auth.user.views import page_views

app_name = 'user'

urlpatterns = [

    path('user/<int:pk>/detail/',
         page_views.detail_view,
         name='detail'),

    path('user/list/',
         page_views.list_view,
         name='list'),
]
