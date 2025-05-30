from django.urls import include, path
from django.views.generic import TemplateView

app_name = 'core'

urlpatterns = [
    path('403/', TemplateView.as_view(template_name='django_spire/403.html'), name='403'),
    path('404/', TemplateView.as_view(template_name='django_spire/404.html'), name='404'),
    path('500/', TemplateView.as_view(template_name='django_spire/500.html'), name='500'),
    path('maintenance/', TemplateView.as_view(template_name='django_spire/maintenance.html'), name='maintenance')
]
