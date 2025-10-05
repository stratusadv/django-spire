from django.urls import path

from django_spire.ai.sms import views

app_name = 'sms'

urlpatterns = [
    path('webhook/', views.webhook_view, name='webhook'),
]
