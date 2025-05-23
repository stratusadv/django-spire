from django.urls import path

from django_spire.auth.group.views import form_views

app_name = 'form'

# Group
urlpatterns = [
    path('<int:pk>/update/',
         form_views.group_form_view,
         name='update'),
    path('create/',
         form_views.group_form_view,
         name='create'),
    path('permission/<int:pk>/delete/',
         form_views.group_delete_form_view,
         name='delete'),
]

# Group User
urlpatterns += [
    path('<int:pk>/user/update/',
         form_views.group_user_form_view,
         name='user_update'),

    path('permission/<int:group_pk>/user/<int:pk>/delete/',
         form_views.group_delete_user_form_view,
         name='user_delete'),
]

