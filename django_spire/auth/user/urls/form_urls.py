from django.urls import path

from django_spire.auth.user.views import form_views

app_name = 'user'

urlpatterns = [
    path('register/user/',
         form_views.register_form_view,
         name='register_form'),

    path('user/<int:pk>/form',
         form_views.form_view,
         name='edit'),

    path('user/<int:pk>/toggle/form/',
         form_views.status_form_view,
         name='status_form'),

    path('user/<int:pk>/group/form/',
         form_views.group_form_view,
         name='group_form'),
]
