from django.urls import path

from test_project.app.home.views import page_views


app_name = 'page'

urlpatterns = [
    path('', page_views.home_view, name='home'),
    path('markdown/', page_views.markdown_demo_view, name='markdown_demo'),
    path('chart/', page_views.chart_demo_view, name='chart_demo'),
    path('restricted/', page_views.restricted_view, name='restricted'),
    path(
        'restricted/<int:pk>/detail/',
        page_views.restricted_detail_view,
        name='restricted_detail',
    ),
    path('restricted/submit/', page_views.restricted_submit_view, name='restricted_submit'),
    path(
        'restricted/django/login/',
        page_views.restricted_django_login_view,
        name='restricted_django_login',
    ),
    path(
        'restricted/django/permission/',
        page_views.restricted_django_permission_view,
        name='restricted_django_permission',
    ),
]
