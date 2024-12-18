from django.urls import path

from django_spire.user_account import views

app_name = 'user_account'

urlpatterns = [
    path('register/user/',
         views.register_user_form_view,
         name='register_user_form'),

    path('user/<int:pk>/detail/',
         views.user_detail_page_view,
         name='detail'),

    path('user/list/',
         views.user_list_page_view,
         name='list'),

    path('user/<int:pk>/form',
         views.user_form_page_view,
         name='form'),

    path('user/<int:pk>/toggle/form/',
         views.user_status_form_page_view,
         name='toggle_user_status'),
]
