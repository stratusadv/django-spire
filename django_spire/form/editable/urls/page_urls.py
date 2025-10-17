from django.urls import path

from django_spire.form.editable.views import page_views

app_name = 'page'

urlpatterns = [
    path('dashboard/', page_views.dashboard_view, name='dashboard')
]
