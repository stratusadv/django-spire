from django.urls import path

from django_spire.auth.user.views import page_views, form_views

app_name = 'form'

urlpatterns = [
    path('register/',
         form_views.user_register_form_view,
         name='register'),

    path('<int:pk>/update/',
         form_views.user_form_view,
         name='update'),

    path('<int:pk>/toggle_status/',
         form_views.user_toggle_status_form_view,
         name='toggle_status'),
]
