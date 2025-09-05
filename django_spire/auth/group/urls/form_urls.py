from django.urls import path

from django_spire.auth.group.views import form_views


app_name = 'form'

# Group
urlpatterns = [
    path('group/form', form_views.form_view, name='add'),
    path('group/<int:pk>/form', form_views.form_view, name='update'),
    path('group/<int:pk>/delete/form', form_views.delete_form_view, name='delete'),
]

# Group User
urlpatterns += [
    path('group/<int:pk>/user/form', form_views.user_form_view, name='user'),
    path('group/<int:group_pk>/user/<int:pk>/form',
         form_views.group_remove_user_form_view,
         name='user_remove'),
]
