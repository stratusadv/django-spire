from django.urls import path

from django_spire.permission import views


app_name = 'permission'

# Group
urlpatterns = [
    path('group/<int:pk>/form',
         views.group_form_view,
         name='group_form'),

    path('group/<int:pk>/delete/form',
         views.group_delete_form_view,
         name='group_delete_form'),

    path('group/<int:pk>/detail/',
         views.group_detail_view,
         name='group_detail'),

    path('group/list/',
         views.group_list_view,
         name='group_list'),

    path('group/<int:pk>/permission/<str:app_name>/ajax/',
         views.group_permission_form_ajax,
         name='group_permission_ajax'),

    path('group/<int:pk>/app/<str:app_name>/special/role/ajax/',
         views.group_special_role_form_ajax,
         name='group_special_role_ajax'),
]

# Group User
urlpatterns += [
    path('group/<int:pk>/user/form',
         views.group_user_form_view,
         name='group_user_form'),

    path('group/<int:group_pk>/user/<int:pk>/form',
         views.group_remove_user_form_view,
         name='group_user_remove_form'),
]
