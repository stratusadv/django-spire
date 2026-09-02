from django.urls import path

from test_project.app.showcase.views import page_views

app_name = 'page'

urlpatterns = [
    path('', page_views.form_view, name='form'),
    path('<int:pk>/', page_views.form_view, name='form'),
]
