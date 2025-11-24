from django.urls import path

from test_project.apps.lazy_tabs.views import template_views


app_name = 'template'

urlpatterns = [
    path('tab/overview/', template_views.tab_overview_view, name='tab_overview'),
    path('tab/details/', template_views.tab_details_view, name='tab_details'),
    path('tab/settings/', template_views.tab_settings_view, name='tab_settings'),
    path('tab/profile/', template_views.tab_profile_view, name='tab_profile'),
    path('tab/activity/', template_views.tab_activity_view, name='tab_activity'),
]
