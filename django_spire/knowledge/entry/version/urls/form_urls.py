from django.urls import path

from django_spire.knowledge.entry.version.views import form_views


app_name = 'form'

urlpatterns = [
    path('<int:pk>/update/', form_views.update_form_view, name='update'),
]
