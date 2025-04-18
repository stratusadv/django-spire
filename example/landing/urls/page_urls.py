from django.urls import path, include

from example.landing.views import page_views


app_name = 'pages'

urlpatterns = [
    path('', page_views.landing_page_view, name='landing'),
]
