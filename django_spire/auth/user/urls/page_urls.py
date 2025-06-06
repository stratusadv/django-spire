from django.urls import path

from django_spire.auth.user.views import page_views

app_name = 'user_account'

urlpatterns = [
    path('register/user/',
         page_views.register_user_form_view,
         name='register_user_form'),

    path('user/<int:pk>/detail/',
         page_views.user_detail_page_view,
         name='detail'),

    path('user/list/',
         page_views.user_list_page_view,
         name='list'),

    path('user/<int:pk>/form',
         page_views.user_form_page_view,
         name='form'),

    path('user/<int:pk>/toggle/form/',
         page_views.user_status_form_page_view,
         name='toggle_user_status'),
]
