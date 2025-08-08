from django.urls import path

from test_project.apps.theme.views import page_views

app_name = 'page'
urlpatterns = [
    path('dashboard/', page_views.dashboard_view, name='dashboard'),
    path('colors/', page_views.colors_view, name='colors'),
    path('typography/', page_views.typography_view, name='typography'),
    path('buttons/', page_views.buttons_view, name='buttons'),
    path('badges/', page_views.badges_view, name='badges'),
    path('borders/', page_views.borders_view, name='borders'),
]
