from django.urls import path

from test_project.apps.lazy_tabs.views import template_views


app_name = 'template'

urlpatterns = [
    path('tab/overview/', template_views.tab_overview_view, name='tab_overview'),
    path('tab/details/', template_views.tab_details_view, name='tab_details'),
    path('tab/settings/', template_views.tab_settings_view, name='tab_settings'),

    path('tab/profile/', template_views.tab_profile_view, name='tab_profile'),
    path('tab/activity/', template_views.tab_activity_view, name='tab_activity'),

    path('tab/items/', template_views.tab_items_view, name='tab_items'),
    path('tab/table/', template_views.tab_table_view, name='tab_table'),

    path('items/', template_views.items_view, name='items'),
    path('rows/', template_views.rows_view, name='rows'),
]
