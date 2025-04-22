from django.urls import path

from django_spire.auth.group.views import page_views


app_name = 'page'

# Group
urlpatterns = [
    path('group/<int:pk>/form',
         page_views.group_form_view,
         name='group_form'),

    path('group/<int:pk>/delete/form',
         page_views.group_delete_form_view,
         name='group_delete_form'),

    path('group/<int:pk>/detail/',
         page_views.group_detail_view,
         name='group_detail'),

    path('group/list/',
         page_views.group_list_view,
         name='group_list'),

    path('group/<int:pk>/permission/<str:app_name>/ajax/',
         page_views.group_permission_form_ajax,
         name='group_permission_ajax'),

    path('group/<int:pk>/app/<str:app_name>/special/role/ajax/',
         page_views.group_special_role_form_ajax,
         name='group_special_role_ajax'),
]

# Group User
urlpatterns += [
    path('group/<int:pk>/user/form',
         page_views.group_user_form_view,
         name='group_user_form'),

    path('group/<int:group_pk>/user/<int:pk>/form',
         page_views.group_remove_user_form_view,
         name='group_user_remove_form'),
]
