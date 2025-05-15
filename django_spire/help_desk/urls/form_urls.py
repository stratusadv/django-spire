from django.urls import path

from django_spire.help_desk.views import form_views

app_name = 'form'

urlpatterns = [
    path('update/<int:pk>/', form_views.ticket_form_view, name='update'),
    path('create/', form_views.ticket_form_view, name='create')
]
